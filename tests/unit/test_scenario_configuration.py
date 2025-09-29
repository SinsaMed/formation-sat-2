"""Unit tests for the scenario configuration discovery and loading helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from sim.scripts import configuration, scenario_execution


def test_tehran_scenario_path_can_be_resolved() -> None:
    """The resolver should find the canonical Tehran scenario file."""

    scenario_path = configuration.resolve_scenario_path("tehran_daily_pass")
    assert scenario_path.is_file()
    assert scenario_path.name == "tehran_daily_pass.json"


def test_tehran_scenario_payload_constraints_are_loaded() -> None:
    """Loading the scenario yields the expected payload limitations and timing."""

    scenario = configuration.load_scenario("tehran_daily_pass")
    metadata = scenario["metadata"]
    assert metadata["scenario_name"] == "Tehran Daily Pass"
    assert metadata["region"]["city"] == "Tehran"

    imager_constraints = scenario["payload_constraints"]["imager"]
    assert imager_constraints["max_off_nadir_deg"] == pytest.approx(25.0)
    assert imager_constraints["required_ground_sample_distance_m"] == pytest.approx(1.0)

    windows = scenario["timing"]["daily_access_windows"]
    assert any(window["label"] == "Morning Imaging" for window in windows)
    assert scenario["timing"]["planning_horizon"]["start_utc"].startswith("2026-03-21")


def test_loaded_scenario_is_accepted_by_simulation_entry_point(tmp_path: Path) -> None:
    """The scenario runner should emit artefacts for the canonical configuration."""

    scenario = configuration.load_scenario("tehran_daily_pass")
    results = scenario_execution.run_scenario(
        scenario,
        output_directory=tmp_path / "products",
    )

    assert results["configuration_summary"]["identifier"] == "tehran_daily_pass"
    assert results["metrics"]["node_count"] == pytest.approx(2.0)
