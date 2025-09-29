"""Integration-style checks for the simulation script scaffolding."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Mapping, MutableMapping

import pytest

from sim.scripts import baseline_generation, metric_extraction, scenario_execution


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


def test_metric_extraction_stub_requires_implementation(
    reference_outputs: Mapping[str, object],
) -> None:
    """Metric extraction should also signal its placeholder status."""

    data_bundle = {
        "scenario_results": reference_outputs,
        "baseline": {"ephemeris": reference_outputs["ephemeris_stub"]},
    }
    with pytest.raises(NotImplementedError, match="Metric extraction scaffolding"):
        metric_extraction.extract_metrics(data_bundle)
