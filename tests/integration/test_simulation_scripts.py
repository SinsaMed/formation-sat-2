"""Integration-style checks for the simulation script scaffolding."""

from __future__ import annotations

import importlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Mapping

import pytest

from sim.scripts import baseline_generation, metric_extraction, scenario_execution

metrics_module = importlib.import_module("sim.scripts.extract_metrics")


def test_scenario_runner_produces_summary(
    tmp_path: Path,
    scenario_configuration: Mapping[str, object],
) -> None:
    """Scenario execution should return a structured summary and artefact path."""

    results = scenario_execution.run_scenario(
        scenario_configuration,
        output_directory=tmp_path / "products",
    )

    expected_stages = [
        "access_nodes",
        "mission_phases",
        "two_body_propagation",
        "high_fidelity_j2_drag_propagation",
        "metric_extraction",
    ]
    if results.get("artefacts", {}).get("stk_export_directory"):
        expected_stages.append("stk_export")
    assert results["stage_sequence"] == expected_stages

    artefact = results["artefacts"]["summary_path"]
    assert artefact is not None
    summary_path = Path(artefact)
    assert summary_path.exists()

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["metrics"]["phase_count"] >= 1.0
    assert payload["propagation"]["two_body"]["model"] == "two_body"
    monte_carlo = payload["propagation"]["j2_drag"].get("monte_carlo", {})
    if monte_carlo:
        assert "centroid_abs_cross_track_km_p95" in monte_carlo
        assert "centroid_abs_cross_track_km_mean" in monte_carlo
        assert monte_carlo["centroid_abs_cross_track_km_p95"] == pytest.approx(
            monte_carlo["centroid_abs_cross_track_km"]["p95"]
        )
        assert monte_carlo["centroid_abs_cross_track_km_mean"] == pytest.approx(
            monte_carlo["centroid_abs_cross_track_km"]["mean"]
        )


def test_baseline_stub_still_raises_not_implemented(
    scenario_configuration: Mapping[str, object],
) -> None:
    """Baseline generation remains a placeholder pending future work."""

    with pytest.raises(
        NotImplementedError,
        match="Baseline generation scaffolding pending implementation.",
    ):
        baseline_generation.generate_baseline(
            scenario_configuration,
            context={"export_format": "stk"},
        )


def test_scenario_runner_cli_smoke(tmp_path: Path) -> None:
    """The command-line interface should complete a smoke run."""

    output_dir = tmp_path / "cli"
    command = [
        sys.executable,
        "-m",
        "sim.scripts.run_scenario",
        "tehran_triangle",
        "--output-dir",
        str(output_dir),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=True)
    assert "Executed scenario" in completed.stdout
    summary_path = output_dir / "scenario_summary.json"
    assert summary_path.exists()


def test_metric_extraction_wrapper_generates_summary(
    synthetic_metric_inputs: Mapping[str, object],
) -> None:
    """The compatibility wrapper should expose the richer metric outputs."""

    bundle = synthetic_metric_inputs["data_bundle"].copy()
    metrics = metric_extraction.extract_metrics(bundle)
    assert metrics["window_statistics"]["count"] == pytest.approx(3.0)
    assert "triangle_geometry" in metrics
    assert metrics["delta_v"]["total_delta_v_mps"] == pytest.approx(0.5)

    rich_metrics = metrics_module.extract_metrics(bundle)
    assert rich_metrics.window_statistics["mean_duration_s"] == pytest.approx(90.0)


def test_triangle_cli_produces_stk_outputs(tmp_path: Path) -> None:
    """The dedicated triangle simulation should emit summary and STK artefacts."""

    output_dir = tmp_path / "triangle"
    command = [
        sys.executable,
        "-m",
        "sim.scripts.run_triangle",
        "--output-dir",
        str(output_dir),
    ]
    subprocess.run(command, check=True, capture_output=True, text=True)

    summary_path = output_dir / "triangle_summary.json"
    assert summary_path.exists()
    stk_dir = output_dir / "stk"
    assert stk_dir.exists()
    assert list(stk_dir.glob("*.e"))

    maintenance_csv = output_dir / "maintenance_summary.csv"
    command_csv = output_dir / "command_windows.csv"
    injection_csv = output_dir / "injection_recovery.csv"
    drag_csv = output_dir / "drag_dispersion.csv"
    plot_path = output_dir / "injection_recovery_cdf.svg"

    assert maintenance_csv.exists()
    assert command_csv.exists()
    assert injection_csv.exists()
    assert drag_csv.exists()
    assert plot_path.exists()

    maintenance_header = maintenance_csv.read_text(encoding="utf-8").splitlines()[0]
    assert "annual_delta_v_mps" in maintenance_header
    command_header = command_csv.read_text(encoding="utf-8").splitlines()[0]
    assert "window_index" in command_header
    injection_header = injection_csv.read_text(encoding="utf-8").splitlines()[0]
    assert "delta_v_mps" in injection_header
    drag_header = drag_csv.read_text(encoding="utf-8").splitlines()[0]
    assert "ground_distance_delta_km" in drag_header
