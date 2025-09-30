"""Asynchronous orchestration of subprocess-based runs for the web service."""

from __future__ import annotations

import asyncio
import itertools
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncIterator, Dict, Iterable, List, Mapping, Optional, Sequence


@dataclass(slots=True)
class SubprocessJob:
    """Representation of a managed subprocess run."""

    job_id: str
    command: Sequence[str]
    cwd: Optional[Path] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    process: asyncio.subprocess.Process | None = field(init=False, default=None)
    status: str = field(init=False, default="pending")
    returncode: Optional[int] = field(init=False, default=None)
    started_at: Optional[datetime] = field(init=False, default=None)
    completed_at: Optional[datetime] = field(init=False, default=None)
    _queue: asyncio.Queue[str] = field(init=False, default_factory=asyncio.Queue)
    _history: List[str] = field(init=False, default_factory=list)
    _done: asyncio.Event = field(init=False, default_factory=asyncio.Event)
    _started: asyncio.Event = field(init=False, default_factory=asyncio.Event)
    _runner_task: asyncio.Task[None] | None = field(init=False, default=None)

    async def start(self) -> None:
        """Launch the subprocess and begin streaming its output."""

        if self._runner_task is not None:
            return
        self._runner_task = asyncio.create_task(self._run(), name=f"job-{self.job_id}")
        await self._started.wait()

    async def wait_completed(self) -> None:
        """Await subprocess completion."""

        await self._done.wait()

    async def cancel(self) -> None:
        """Terminate the subprocess if it is active."""

        if self.process is None or self.status not in {"running", "pending"}:
            return
        self.status = "cancelling"
        self._record("[status] Cancelling job…")
        try:
            self.process.terminate()
            await asyncio.wait_for(self.process.wait(), timeout=10)
        except ProcessLookupError:
            pass
        except asyncio.TimeoutError:
            self._record("[status] Termination timeout reached; sending SIGKILL.")
            self.process.kill()
            await self.process.wait()
        finally:
            self.returncode = self.process.returncode
            self.status = "cancelled"
            self.completed_at = datetime.now(timezone.utc)
            self._record("[status] Job cancelled by user.")
            self._done.set()

    async def iter_lines(self) -> AsyncIterator[str]:
        """Yield buffered history before streaming live updates."""

        for entry in self._history:
            yield entry
        while True:
            if self._done.is_set() and self._queue.empty():
                break
            try:
                entry = await asyncio.wait_for(self._queue.get(), timeout=0.5)
            except asyncio.TimeoutError:
                continue
            yield entry

    def snapshot(self) -> Mapping[str, object]:
        """Serialise the job metadata for API responses."""

        payload: Dict[str, object] = {
            "job_id": self.job_id,
            "command": list(self.command),
            "status": self.status,
            "created_at": self.created_at.isoformat().replace("+00:00", "Z"),
        }
        if self.returncode is not None:
            payload["returncode"] = self.returncode
        if self.started_at is not None:
            payload["started_at"] = self.started_at.isoformat().replace("+00:00", "Z")
        if self.completed_at is not None:
            payload["completed_at"] = self.completed_at.isoformat().replace("+00:00", "Z")
        return payload

    async def _run(self) -> None:
        try:
            self.process = await asyncio.create_subprocess_exec(
                *self.command,
                cwd=str(self.cwd) if self.cwd else None,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except Exception as error:  # pragma: no cover - defensive branch
            self.status = "failed"
            self._record(f"[error] Failed to start process: {error}")
            self.completed_at = datetime.now(timezone.utc)
            self._started.set()
            self._done.set()
            return

        self.status = "running"
        self.started_at = datetime.now(timezone.utc)
        self._started.set()
        streams: List[asyncio.Task[None]] = []
        if self.process.stdout:
            streams.append(asyncio.create_task(self._consume_stream(self.process.stdout, "stdout")))
        if self.process.stderr:
            streams.append(asyncio.create_task(self._consume_stream(self.process.stderr, "stderr")))
        returncode = await self.process.wait()
        self.returncode = returncode
        self.completed_at = datetime.now(timezone.utc)
        self.status = "completed" if returncode == 0 else "failed"
        if streams:
            await asyncio.gather(*streams, return_exceptions=True)
        self._record(f"[status] Process finished with code {returncode}.")
        self._done.set()

    async def _consume_stream(self, stream: asyncio.StreamReader, label: str) -> None:
        while True:
            line = await stream.readline()
            if not line:
                break
            text = line.decode("utf-8", errors="replace").rstrip("\n")
            self._record(f"[{label}] {text}")

    def _record(self, message: str) -> None:
        self._history.append(message)
        if len(self._history) > 5000:
            del self._history[: len(self._history) - 5000]
        self._queue.put_nowait(message)


class JobManager:
    """Manage lifecycle of subprocess-backed jobs for the web frontend."""

    def __init__(self) -> None:
        self._jobs: Dict[str, SubprocessJob] = {}
        self._lock = asyncio.Lock()
        self._counter = itertools.count(1)

    async def create_job(self, command: Iterable[str], cwd: Optional[Path] = None) -> SubprocessJob:
        """Instantiate and start a new subprocess job."""

        job_id = f"job_{next(self._counter):04d}"
        job = SubprocessJob(job_id=job_id, command=tuple(command), cwd=cwd)
        async with self._lock:
            self._jobs[job_id] = job
        await job.start()
        return job

    async def get_job(self, job_id: str) -> Optional[SubprocessJob]:
        """Return a job by identifier if it exists."""

        async with self._lock:
            return self._jobs.get(job_id)

    async def list_jobs(self) -> List[Mapping[str, object]]:
        """Return metadata snapshots for all known jobs ordered by recency."""

        async with self._lock:
            jobs = list(self._jobs.values())
        jobs.sort(key=lambda item: item.created_at, reverse=True)
        return [job.snapshot() for job in jobs]

    async def cancel_job(self, job_id: str) -> bool:
        """Attempt to cancel the specified job."""

        job = await self.get_job(job_id)
        if job is None:
            return False
        await job.cancel()
        return True

    async def prune_completed(self, keep: int = 10) -> None:
        """Remove completed jobs beyond the retention limit."""

        async with self._lock:
            completed = [job for job in self._jobs.values() if job.status in {"completed", "failed", "cancelled"}]
            completed.sort(key=lambda item: item.completed_at or item.created_at, reverse=True)
            for job in completed[keep:]:
                self._jobs.pop(job.job_id, None)

