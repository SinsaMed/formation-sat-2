"""Integration-style checks for the simulation script scaffolding."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Mapping, MutableMapping

import pytest

from sim.scripts import baseline_generation, metric_extraction, scenario_execution
from sim.scripts import extract_metrics as metrics_module


@pytest.mark.parametrize(
    ("callable_under_test", "kwargs", "message"),
    [
        (
            scenario_execution.run_scenario,
            {"output_directory": Path("/tmp/nonexistent")},
            "Scenario execution scaffolding pending implementation.",
        ),
        (
            baseline_generation.generate_baseline,
            {"context": {"export_format": "stk"}},
            "Baseline generation scaffolding pending implementation.",
        ),
    ],
)
def test_simulation_entry_points_raise_not_implemented(
    callable_under_test: Callable[..., MutableMapping[str, object]],
    kwargs: Mapping[str, object],
    message: str,
    scenario_configuration: Mapping[str, object],
) -> None:
    """The current scaffolding should raise consistent ``NotImplementedError`` messages."""

    with pytest.raises(NotImplementedError, match=message):
        callable_under_test(scenario_configuration, **kwargs)


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
