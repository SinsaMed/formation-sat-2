"""Unit tests for the baseline comparison helper."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests import baseline_compare


@pytest.fixture()
def temp_result_pair(tmp_path: Path) -> tuple[Path, Path]:
    """Create paired baseline and candidate directories populated with JSON."""

    baseline_dir = tmp_path / "baseline"
    candidate_dir = tmp_path / "candidate"
    baseline_dir.mkdir()
    candidate_dir.mkdir()

    baseline_payload = {
        "identifier": "AP-LEAD",
        "metrics": {"delta_v_mps": 0.12345, "coverage": 96.2},
        "state_vector": [1.0, 2.0, 3.0],
    }
    (baseline_dir / "nominal.json").write_text(json.dumps(baseline_payload), encoding="utf-8")
    (candidate_dir / "nominal.json").write_text(json.dumps(baseline_payload), encoding="utf-8")

    return baseline_dir, candidate_dir


def test_identical_payloads_produce_no_differences(temp_result_pair: tuple[Path, Path]) -> None:
    """When the payloads match, the comparison yields no diagnostic messages."""

    baseline_dir, candidate_dir = temp_result_pair
    config = baseline_compare.ComparisonConfig()
    differences = baseline_compare.run_comparison(
        baseline_dir=baseline_dir,
        candidate_dir=candidate_dir,
        config=config,
        allow_missing=False,
    )
    assert differences == []


def test_tolerance_controls_numeric_comparison(temp_result_pair: tuple[Path, Path]) -> None:
    """Numeric deviations smaller than the tolerance are ignored."""

    baseline_dir, candidate_dir = temp_result_pair
    updated_payload = json.loads((candidate_dir / "nominal.json").read_text(encoding="utf-8"))
    updated_payload["metrics"]["delta_v_mps"] += 5e-10
    (candidate_dir / "nominal.json").write_text(json.dumps(updated_payload), encoding="utf-8")

    config = baseline_compare.ComparisonConfig(absolute_tolerance=1e-9, relative_tolerance=1e-6)
    differences = baseline_compare.run_comparison(
        baseline_dir=baseline_dir,
        candidate_dir=candidate_dir,
        config=config,
        allow_missing=False,
    )
    assert differences == []


def test_large_numeric_differences_are_reported(temp_result_pair: tuple[Path, Path]) -> None:
    """Significant numeric deviations generate an explanatory message."""

    baseline_dir, candidate_dir = temp_result_pair
    updated_payload = json.loads((candidate_dir / "nominal.json").read_text(encoding="utf-8"))
    updated_payload["metrics"]["delta_v_mps"] += 1e-3
    (candidate_dir / "nominal.json").write_text(json.dumps(updated_payload), encoding="utf-8")

    config = baseline_compare.ComparisonConfig(absolute_tolerance=1e-6, relative_tolerance=1e-6)
    differences = baseline_compare.run_comparison(
        baseline_dir=baseline_dir,
        candidate_dir=candidate_dir,
        config=config,
        allow_missing=False,
    )
    assert any("Numeric deviation" in message for message in differences)


def test_missing_candidate_directory_is_tolerated_when_allowed(tmp_path: Path) -> None:
    """The helper issues guidance rather than failing when the candidate set is absent."""

    baseline_dir = tmp_path / "baseline"
    baseline_dir.mkdir()
    payload = {"status": "nominal"}
    (baseline_dir / "state.json").write_text(json.dumps(payload), encoding="utf-8")

    config = baseline_compare.ComparisonConfig()
    differences = baseline_compare.run_comparison(
        baseline_dir=baseline_dir,
        candidate_dir=tmp_path / "candidate",
        config=config,
        allow_missing=True,
    )
    assert differences == [
        "Candidate directory absent; comparison skipped pending first nominal simulation export."
    ]
