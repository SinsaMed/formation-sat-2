"""Create a timestamped documentation summary for automation smoke tests."""

from __future__ import annotations

import argparse
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


def parse_args(args: Iterable[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments for the summary generator."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artefacts/docs"),
        help="Directory in which to publish the generated summary.",
    )
    return parser.parse_args(args)


def write_summary(output_dir: Path) -> Path:
    """Write a brief automation summary into ``output_dir``."""

    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "summary.txt"
    summary = textwrap.dedent(
        f"""
        Generated on {datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')}
        This placeholder confirms that automated documentation exports are wired
        into the pipeline pending a full Sphinx-based build.
        """
    ).strip() + "\n"
    summary_path.write_text(summary, encoding="utf-8")
    return summary_path


def main(args: Iterable[str] | None = None) -> int:
    """Entrypoint used by the Makefile and CI workflow."""

    namespace = parse_args(args)
    summary_path = write_summary(namespace.output_dir)
    print(f"Documentation summary written to {summary_path}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
