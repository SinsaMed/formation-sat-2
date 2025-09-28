"""Scenario execution workflow scaffolding.

This module prepares the foundations for running formation-flying
scenarios that must remain interoperable with Systems Tool Kit (STK)
11.2. Once implemented, it will provide utilities to configure
simulation inputs, dispatch runs, and catalogue outputs in formats that
``tools/stk_export.py`` can serialise.

Usage
======
1. Instantiate a scenario configuration dictionary describing the
   spacecraft constellation, propagator preferences, and time bounds.
2. Call :func:`prepare_scenario_context` to translate the configuration
   into executable artefacts (for example, ephemeris files or STK
   scenario templates).
3. Supply the resulting context to :func:`execute_scenario` alongside an
   output directory to run the simulation and persist results for later
   analysis.

Inputs
=======
``scenario_config``
    A dictionary containing mission design parameters, including STK
    scenario metadata, satellite identifiers, and relevant environmental
    models.
``output_directory``
    A filesystem path pointing to where STK-compatible outputs should be
    written. The location must be accessible for validation with
    ``tools/stk_export.py``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Mapping


def prepare_scenario_context(scenario_config: Mapping[str, object]) -> Dict[str, object]:
    """Convert a scenario configuration into executable context data.

    Parameters
    ----------
    scenario_config:
        Mission design parameters that will eventually be mapped onto STK
        11.2 scenario files. Typical entries will include orbit
        definitions, force models, and numerical tolerances.

    Returns
    -------
    dict
        A dictionary describing the prepared artefacts (for instance,
        resolved file paths or propagated initial conditions). The
        structure will be defined in subsequent development stages.

    Notes
    -----
    The function currently raises :class:`NotImplementedError` until a
    concrete implementation is provided in a follow-on task. When
    developing the implementation, ensure that any generated files are
    validated with ``tools/stk_export.py`` to preserve STK
    interoperability.
    """

    raise NotImplementedError(
        "Scenario context preparation is pending implementation."
    )


def execute_scenario(context: Mapping[str, object], output_directory: Path | str) -> None:
    """Run the configured scenario and export STK-compatible products.

    Parameters
    ----------
    context:
        The prepared context produced by :func:`prepare_scenario_context`.
        The mapping should contain all data needed to initialise the STK
        scenario as well as bookkeeping information for subsequent
        analysis.
    output_directory:
        Destination directory for STK-ready outputs such as ephemerides,
        attitude profiles, and log files.

    Raises
    ------
    NotImplementedError
        The execution logic will be introduced in a later task. The
        placeholder reminds developers to supply STK validation hooks
        once the actual propagators and exporters are connected.
    """

    _ = Path(output_directory)
    raise NotImplementedError("Scenario execution is pending implementation.")
