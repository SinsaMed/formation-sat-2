"""Constellation-level utilities for the formation flying mission analyses.

The module collates reference-frame transformations, simple geometric
estimators, and relative orbital element helpers that are frequently required
when validating Systems Tool Kit (STK) data exchanges for the mission
engineering studies documented in :mod:`docs`.
"""

from . import frames, geometry, roe

__all__ = [
    "frames",
    "geometry",
    "roe",
]
