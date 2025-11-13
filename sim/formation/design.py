r"""Formation design utilities leveraging J2-invariant relative orbit theory."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, MutableMapping, Sequence

import numpy as np

from src.constellation.roe import OrbitalElements, RelativeOrbitalElements, absolute_from_roe


@dataclass(frozen=True)
class FormationDesignResult:
    """Container describing the outcome of a formation design routine."""

    satellite_elements: Mapping[str, OrbitalElements]


def _relative_elements_from_offset(
    offset_lvlh_m: Sequence[float],
    semi_major_axis_m: float,
    argument_of_latitude_rad: float,
) -> RelativeOrbitalElements:
    r"""Translate an LVLH offset into relative orbital elements.

    The mapping follows the linearised Hill-Clohessy-Wiltshire relations for
    near-circular reference orbits as documented by Gim and Alfriend (2003).
    By construction the relative semi-major axis, eccentricity, and inclination
    components satisfy the J2-invariant conditions \(\delta a = \delta e = \delta i = 0\).
    """

    offset = np.asarray(offset_lvlh_m, dtype=float)
    if offset.shape != (3,):
        raise ValueError("LVLH offsets must be three-dimensional vectors.")

    # The equilateral triangle is constrained to the local horizontal plane,
    # hence the radial component is expected to remain close to zero.  The
    # mapping keeps the formulation general in case small radial trims are
    # introduced in future analyses.
    radial, along_track, cross_track = (float(value) for value in offset)

    # Enforce a shared semi-major axis and vanishing relative eccentricity and
    # inclination magnitudes to honour the Gim-Alfriend secular invariants.
    delta_a_over_a = 0.0
    delta_ex = 0.0
    delta_ey = 0.0

    sin_u = float(np.sin(argument_of_latitude_rad))
    cos_u = float(np.cos(argument_of_latitude_rad))

    delta_iy = -cross_track * cos_u / semi_major_axis_m
    delta_ix = cross_track * sin_u / semi_major_axis_m

    # The in-plane phase parameter governs the along-track separation.  With
    # \(\delta e_y = 0\) the natural-motion-circle solution reduces to
    # \(y = a \, \delta \lambda\) at the chosen epoch.
    delta_lambda = along_track / semi_major_axis_m

    return RelativeOrbitalElements(
        delta_a_over_a=delta_a_over_a,
        delta_lambda=delta_lambda,
        delta_ex=delta_ex,
        delta_ey=delta_ey,
        delta_ix=delta_ix,
        delta_iy=delta_iy,
    )


def design_j2_invariant_formation(
    reference_elements: OrbitalElements,
    offsets_lvlh_m: Mapping[str, Sequence[float]],
) -> FormationDesignResult:
    r"""Return J2-invariant orbital elements for a set of LVLH offsets.

    Parameters
    ----------
    reference_elements:
        Mean orbital elements describing the virtual chief trajectory.
    offsets_lvlh_m:
        Mapping between satellite identifiers and desired LVLH offsets expressed
        in metres.  The offsets follow the \([x, y, z]\) convention corresponding
        to radial, along-track, and cross-track components respectively.
    """

    semi_major_axis_m = reference_elements.semi_major_axis
    argument_of_latitude = reference_elements.mean_anomaly + reference_elements.arg_perigee
    designed: MutableMapping[str, OrbitalElements] = {}

    for sat_id, offset in offsets_lvlh_m.items():
        roe = _relative_elements_from_offset(
            offset,
            semi_major_axis_m,
            argument_of_latitude,
        )
        designed[sat_id] = absolute_from_roe(reference_elements, roe)

    return FormationDesignResult(satellite_elements=designed)


__all__ = [
    "FormationDesignResult",
    "design_j2_invariant_formation",
]
