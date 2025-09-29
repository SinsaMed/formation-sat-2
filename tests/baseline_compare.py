"""Baseline regression comparison utilities for simulation artefacts.

The module compares candidate simulation results against the stored canonical
baselines located in ``tests/data/baselines``. It performs a recursive
structural and numerical diff with configurable absolute and relative
thresholds, ignoring keys whose variability would otherwise generate false
positives (for instance timestamps). The script is intentionally lightweight so
that it can run inside both the pytest suite and the continuous integration
workflow without external dependencies.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections.abc import Iterable, Iterator, Mapping, MutableSequence, Sequence
from dataclasses import dataclass
from fnmatch import fnmatchcase
from pathlib import Path

import numbers

DEFAULT_ABSOLUTE_TOLERANCE = 1e-9
DEFAULT_RELATIVE_TOLERANCE = 1e-6


@dataclass(frozen=True)
class ComparisonConfig:
    """Configuration container describing comparison tolerances and filters."""

    absolute_tolerance: float = DEFAULT_ABSOLUTE_TOLERANCE
    relative_tolerance: float = DEFAULT_RELATIVE_TOLERANCE
    ignore_patterns: Sequence[str] = ()

    def should_ignore(self, path: Sequence[str]) -> bool:
        """Return ``True`` when the supplied path matches an ignore pattern."""

        path_string = _normalise_path(path)
        return any(fnmatchcase(path_string, pattern) for pattern in self.ignore_patterns)


def _normalise_path(path: Sequence[str]) -> str:
    """Convert a comparison path into a dotted notation string."""

    components: MutableSequence[str] = []
    for element in path:
        if not components:
            components.append(str(element))
            continue
        if element.startswith("["):
            components[-1] = f"{components[-1]}{element}"
        else:
            components.append(str(element))
    return ".".join(components)


def _iter_json_files(directory: Path) -> Iterator[Path]:
    """Yield JSON files within ``directory`` sorted by name."""

    yield from sorted(path for path in directory.glob("*.json") if path.is_file())


def load_structures(directory: Path) -> Mapping[str, object]:
    """Load JSON artefacts from ``directory`` into a mapping keyed by filename."""

    data: dict[str, object] = {}
    for json_path in _iter_json_files(directory):
        data[json_path.name] = json.loads(json_path.read_text(encoding="utf-8"))
    return data


def compare_mappings(
    candidate: Mapping[str, object],
    baseline: Mapping[str, object],
    *,
    config: ComparisonConfig,
    path: Sequence[str] | None = None,
) -> list[str]:
    """Compare two mappings and return a list of human-readable differences."""

    differences: list[str] = []
    if path is None:
        path = []

    candidate_keys = set(candidate)
    baseline_keys = set(baseline)
    for missing in sorted(baseline_keys - candidate_keys):
        current_path = [*path, missing]
        if config.should_ignore(current_path):
            continue
        differences.append(f"Missing key at { _normalise_path(current_path) }")
    for extra in sorted(candidate_keys - baseline_keys):
        current_path = [*path, extra]
        if config.should_ignore(current_path):
            continue
        differences.append(f"Unexpected key at { _normalise_path(current_path) }")

    for key in sorted(candidate_keys & baseline_keys):
        current_path = [*path, key]
        if config.should_ignore(current_path):
            continue
        differences.extend(
            compare_values(candidate[key], baseline[key], config=config, path=current_path)
        )

    return differences


def compare_sequences(
    candidate: Sequence[object],
    baseline: Sequence[object],
    *,
    config: ComparisonConfig,
    path: Sequence[str],
) -> list[str]:
    """Compare two sequences element by element."""

    differences: list[str] = []
    if len(candidate) != len(baseline):
        differences.append(
            f"Length mismatch at { _normalise_path(path) }: "
            f"candidate {len(candidate)} vs baseline {len(baseline)}"
        )
        return differences

    for index, (candidate_item, baseline_item) in enumerate(zip(candidate, baseline)):
        indexed_path = [*path, f"[{index}]"]
        if config.should_ignore(indexed_path):
            continue
        differences.extend(
            compare_values(candidate_item, baseline_item, config=config, path=indexed_path)
        )

    return differences


def compare_numbers(
    candidate: numbers.Number,
    baseline: numbers.Number,
    *,
    config: ComparisonConfig,
    path: Sequence[str],
) -> list[str]:
    """Compare numeric values using the configured tolerances."""

    if math.isclose(
        float(candidate),
        float(baseline),
        rel_tol=config.relative_tolerance,
        abs_tol=config.absolute_tolerance,
    ):
        return []

    return [
        (
            f"Numeric deviation at { _normalise_path(path) }: "
            f"candidate={candidate!r}, baseline={baseline!r}"
        )
    ]


def compare_values(
    candidate: object,
    baseline: object,
    *,
    config: ComparisonConfig,
    path: Sequence[str],
) -> list[str]:
    """Recursively compare two values according to their types."""

    if isinstance(candidate, Mapping) and isinstance(baseline, Mapping):
        return compare_mappings(candidate, baseline, config=config, path=path)
    if isinstance(candidate, Sequence) and not isinstance(candidate, (str, bytes)):
        if isinstance(baseline, Sequence) and not isinstance(baseline, (str, bytes)):
            return compare_sequences(candidate, baseline, config=config, path=path)
        return [
            (
                f"Type mismatch at { _normalise_path(path) }: "
                f"candidate={type(candidate).__name__}, baseline={type(baseline).__name__}"
            )
        ]
    if isinstance(candidate, numbers.Number) and isinstance(baseline, numbers.Number):
        return compare_numbers(candidate, baseline, config=config, path=path)

    if candidate != baseline:
        return [
            (
                f"Value mismatch at { _normalise_path(path) }: "
                f"candidate={candidate!r}, baseline={baseline!r}"
            )
        ]
    return []


def run_comparison(
    *,
    baseline_dir: Path,
    candidate_dir: Path,
    config: ComparisonConfig,
    allow_missing: bool,
) -> list[str]:
    """Execute the directory-level comparison and return discovered differences."""

    if not baseline_dir.exists():
        raise FileNotFoundError(
            f"Baseline directory '{baseline_dir}' does not exist; initialise baselines first."
        )

    if not candidate_dir.exists():
        if allow_missing:
            return [
                (
                    "Candidate directory absent; comparison skipped pending first nominal "
                    "simulation export."
                )
            ]
        raise FileNotFoundError(
            f"Candidate directory '{candidate_dir}' does not exist; provide simulation outputs."
        )

    baseline_data = load_structures(baseline_dir)
    candidate_data = load_structures(candidate_dir)

    differences: list[str] = []

    for missing in sorted(set(baseline_data) - set(candidate_data)):
        path = [missing]
        if config.should_ignore(path):
            continue
        differences.append(f"Missing candidate file for baseline artefact '{missing}'")

    for extra in sorted(set(candidate_data) - set(baseline_data)):
        path = [extra]
        if config.should_ignore(path):
            continue
        differences.append(f"Unexpected candidate artefact '{extra}' with no baseline")

    for name in sorted(set(baseline_data) & set(candidate_data)):
        path = [name]
        if config.should_ignore(path):
            continue
        differences.extend(
            compare_values(candidate_data[name], baseline_data[name], config=config, path=path)
        )

    return differences


def parse_args(args: Iterable[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments for the comparison utility."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--baseline-dir",
        type=Path,
        default=Path("tests/data/baselines"),
        help="Directory containing canonical baseline JSON artefacts.",
    )
    parser.add_argument(
        "--candidate-dir",
        type=Path,
        required=True,
        help="Directory containing newly generated simulation results to validate.",
    )
    parser.add_argument(
        "--absolute-tolerance",
        type=float,
        default=DEFAULT_ABSOLUTE_TOLERANCE,
        help="Absolute tolerance applied to numeric comparisons.",
    )
    parser.add_argument(
        "--relative-tolerance",
        type=float,
        default=DEFAULT_RELATIVE_TOLERANCE,
        help="Relative tolerance applied to numeric comparisons.",
    )
    parser.add_argument(
        "--ignore",
        dest="ignore_patterns",
        action="append",
        default=[],
        help="Dotted-path patterns to skip during comparison (supports Unix wildcards).",
    )
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="Do not fail when the candidate directory has not been produced yet.",
    )
    return parser.parse_args(args)


def main(args: Iterable[str] | None = None) -> int:
    """Command-line entry point."""

    namespace = parse_args(args)
    config = ComparisonConfig(
        absolute_tolerance=namespace.absolute_tolerance,
        relative_tolerance=namespace.relative_tolerance,
        ignore_patterns=tuple(namespace.ignore_patterns),
    )

    try:
        differences = run_comparison(
            baseline_dir=namespace.baseline_dir,
            candidate_dir=namespace.candidate_dir,
            config=config,
            allow_missing=namespace.allow_missing,
        )
    except FileNotFoundError as exc:  # pragma: no cover - defensive CLI guard.
        print(str(exc), file=sys.stderr)
        return 2

    informative_differences = [diff for diff in differences if not diff.startswith("Candidate directory absent")]
    if informative_differences:
        for message in informative_differences:
            print(message)
        return 1

    for message in differences:
        print(message)
    if not differences:
        print("Baseline comparison succeeded with no differences detected.")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI execution gate.
    raise SystemExit(main())
