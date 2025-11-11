"""Unit tests for the scenario configuration discovery and loading helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from sim.scripts import configuration, scenario_execution


def test_tehran_scenario_path_can_be_resolved() -> None:
    """The resolver should find the canonical Tehran scenario file."""

    scenario_path = configuration.resolve_scenario_path("tehran_triangle")
    assert scenario_path.is_file()
    assert scenario_path.name == "tehran_triangle.json"


def test_tehran_scenario_payload_constraints_are_loaded() -> None:
    scenario = configuration.load_scenario("tehran_triangle")
    metadata = scenario["metadata"]
    assert metadata["scenario_name"] == "Tehran Triangle Formation"








def test_loaded_scenario_is_accepted_by_simulation_entry_point(tmp_path: Path) -> None:
    """The scenario runner should emit artefacts for the canonical configuration."""

    scenario = configuration.load_scenario("tehran_triangle")
    results = scenario_execution.run_scenario(
        scenario,
        output_directory=tmp_path / "products",
    )

    assert results["configuration_summary"]["identifier"] == "Tehran Triangle Formation"
    assert results["metrics"]["node_count"] == pytest.approx(1.0)
