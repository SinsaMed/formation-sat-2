"""Scenario execution entry point delegating to the lightweight pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping, MutableMapping, Optional, Union

from . import run_scenario as scenario_runner

ConfigSource = Union[str, Path, Mapping[str, object]]


def run_scenario(
    config_source: ConfigSource,
    output_directory: Optional[Union[str, Path]] = None,
) -> MutableMapping[str, object]:
    """Execute the scenario pipeline via :mod:`sim.scripts.run_scenario`."""

    return scenario_runner.run_scenario(config_source, output_directory=output_directory)


__all__ = ["run_scenario"]
