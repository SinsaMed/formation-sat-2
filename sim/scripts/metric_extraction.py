"""Metric extraction scaffolding for formation mission assessments.

The module introduces the interface contract for deriving analytical metrics
from simulated or experimentally derived data sets. It will ultimately connect to
STK-compatible exporters and reporting utilities to ensure uniform evaluation of
mission performance across design iterations.

Usage:
    1. Compile a dictionary-like structure containing scenario outputs, baseline
       products, and any ancillary context required for analysis.
    2. Provide the data bundle to :func:`extract_metrics` alongside a specification
       describing the metrics to be evaluated.
    3. Use the returned container to feed reporting pipelines, dashboards, or
       regression test harnesses.

Inputs:
    data_bundle: Mapping containing the scenario outputs and reference materials
        to be interrogated for performance metrics.
    metric_specification: Optional mapping or sequence detailing which metrics
        should be evaluated during processing.
"""

from __future__ import annotations

from typing import Mapping, MutableMapping, Optional, Sequence

from .extract_metrics import extract_metrics as _extract_metrics


def extract_metrics(
    data_bundle: Mapping[str, object],
    metric_specification: Optional[Sequence[str]] = None,
) -> MutableMapping[str, object]:
    """Backwards-compatible wrapper around :mod:`sim.scripts.extract_metrics`."""

    metrics = _extract_metrics(data_bundle, metric_specification)
    return metrics.to_dict()
