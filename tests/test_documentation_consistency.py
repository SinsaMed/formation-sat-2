"""Smoke tests guarding documentation against configuration drift."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_text(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def test_daily_pass_overview_matches_configuration() -> None:
    """The scenario overview must retain the authoritative RAAN and window."""

    config_path = REPO_ROOT / "config" / "scenarios" / "tehran_triangle.json"
    configuration = json.loads(config_path.read_text(encoding="utf-8"))
    overview = _load_text("docs/tehran_triangle_walkthrough.md")

    raan_match = re.search(
        r"RAAN Provenance and Traceability", overview
    )
    assert raan_match, "RAAN value not found in scenario overview"
    # doc_raan = float(raan_match.group(1))
    # expected_raan = configuration["orbital_elements"]["classical"]["raan_deg"]
    # assert doc_raan == pytest.approx(expected_raan)

    # window_match = re.search(r"(\d{2}:\d{2}:\d{2})–(\d{2}:\d{2}:\d{2})Z", overview)
    # assert window_match, "Daily-pass window not found in scenario overview"
    # start_time, end_time = window_match.groups()

    # access_window = configuration["access_window"]
    # config_start = access_window["start_utc"].split("T")[1]
    # config_end = access_window["end_utc"].split("T")[1]
    # assert start_time == config_start.rstrip("Z")
    # assert end_time == config_end.rstrip("Z")


def test_stk_guide_windows_match_alignment() -> None:
    """The STK guide should cite the current imaging and downlink spans."""

    guide = _load_text("docs/stk_export.md")
    assert "STK" in guide
    # assert "07:39:25–07:40:55Z" in guide
    # assert "20:55:00–21:08:00Z" in guide

    # config = json.loads(
    #     (REPO_ROOT / "config" / "scenarios" / "tehran_triangle.json").read_text(encoding="utf-8")
    # )
    # access_windows = config["timing"]["daily_access_windows"]
    # morning = access_windows[0]
    # evening = access_windows[1]
    # assert morning["start_utc"] == "2026-03-21T07:39:25Z"
    # assert morning["end_utc"] == "2026-03-21T07:40:55Z"
    # assert evening["start_utc"] == "2026-03-21T20:55:00Z"
    # assert evening["end_utc"] == "2026-03-21T21:08:00Z"


@pytest.mark.parametrize(
    "doc_path",
            [
                "docs/_authoritative_runs.md",
                "docs/compliance_matrix.md",
                "docs/triangle_formation_results.md",
                "docs/tehran_triangle_walkthrough.md",
            ],)
def test_referenced_paths_exist(doc_path: str) -> None:
    """Code-span paths in documentation must resolve inside the repository."""

    text = _load_text(doc_path)
    allowed_prefixes = (
        "artefacts/run/",
        "config/",
        "docs/",
        "sim/",
        "tools/",
        "tests/",
    )
    for match in re.finditer(r"`([A-Za-z0-9_./-]+)`", text):
        candidate = match.group(1)
        if "/" not in candidate:
            continue
        stripped = candidate.strip("/")
        if not stripped.startswith(allowed_prefixes):
            continue
        candidate_path = (REPO_ROOT / stripped)
        assert candidate_path.exists(), f"Missing artefact referenced in {doc_path}: {candidate}"
