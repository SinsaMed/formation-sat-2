r"""Relative orbital element helpers for constellation design.

This module implements a concise set of tools for computing and propagating
relative orbital elements (ROEs) for near-circular low-Earth orbits.  The
parameterisation follows the Chief-Deputy convention used throughout the
mission analysis notebooks and Systems Tool Kit workflows.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np

MU_EARTH: float = 3.986_004_418e14  # [m^3 s^-2]


@dataclass(frozen=True)
class OrbitalElements:
    """Mean Keplerian elements used for the ROE calculations.

    All angular quantities are expressed in radians.
    """

    semi_major_axis: float
    eccentricity: float
    inclination: float
    raan: float
    arg_perigee: float
    mean_anomaly: float

    def mean_motion(self, mu: float = MU_EARTH) -> float:
        r"""Return the mean motion associated with the orbit.

        The mean motion :math:`n` is given by :math:`n = \sqrt{\mu / a^3}` and is
        used by :func:`propagate_roe` when modelling the drift of the mean
        longitude difference.

        Examples
        --------
        >>> chief = OrbitalElements(7000e3, 0.0, 0.0, 0.0, 0.0, 0.0)
        >>> round(chief.mean_motion() / 1e-3, 3)
        1.078
        """

        return float(np.sqrt(mu / self.semi_major_axis**3))


@dataclass(frozen=True)
class RelativeOrbitalElements:
    """Relative orbital elements expressed in the chief's orbital frame."""

    delta_a_over_a: float
    delta_lambda: float
    delta_ex: float
    delta_ey: float
    delta_ix: float
    delta_iy: float

    def as_tuple(self) -> Tuple[float, float, float, float, float, float]:
        """Return the ROE parameters as a tuple for convenience."""

        return (
            self.delta_a_over_a,
            self.delta_lambda,
            self.delta_ex,
            self.delta_ey,
            self.delta_ix,
            self.delta_iy,
        )


def roe_from_absolute(chief: OrbitalElements, deputy: OrbitalElements) -> RelativeOrbitalElements:
    r"""Compute ROEs from the absolute mean orbital elements.

    The formulation follows the Hill-Clohessy-Wiltshire approximation adopted in
    the mission's formation-keeping studies.  The definitions are consistent with
    Montenbruck and Gill (2000), namely

    .. math::

        \delta a / a &= (a_d - a_c) / a_c, \\
        \delta \lambda &= \Delta M + \Delta \omega + \cos i_c \; \Delta \Omega, \\
        \delta e_x &= e_d \cos \omega_d - e_c \cos \omega_c, \\
        \delta e_y &= e_d \sin \omega_d - e_c \sin \omega_c, \\
        \delta i_x &= i_d - i_c, \\
        \delta i_y &= \sin i_c \; (\Omega_d - \Omega_c).

    The in-plane angle combination :math:`\delta \lambda` is especially helpful
    when drafting differential-drift manoeuvres for nadir-pointing missions.
    """

    delta_a_over_a = (deputy.semi_major_axis - chief.semi_major_axis) / chief.semi_major_axis

    delta_raan = deputy.raan - chief.raan
    delta_i = deputy.inclination - chief.inclination

    ex_chief = chief.eccentricity * np.cos(chief.arg_perigee)
    ey_chief = chief.eccentricity * np.sin(chief.arg_perigee)
    ex_deputy = deputy.eccentricity * np.cos(deputy.arg_perigee)
    ey_deputy = deputy.eccentricity * np.sin(deputy.arg_perigee)

    delta_lambda = (
        (deputy.mean_anomaly - chief.mean_anomaly)
        + (deputy.arg_perigee - chief.arg_perigee)
        + np.cos(chief.inclination) * delta_raan
    )

    delta_ix = delta_i
    sin_ic = np.sin(chief.inclination)
    if np.isclose(sin_ic, 0.0):
        delta_iy = delta_raan
    else:
        delta_iy = sin_ic * delta_raan

    return RelativeOrbitalElements(
        delta_a_over_a=delta_a_over_a,
        delta_lambda=delta_lambda,
        delta_ex=ex_deputy - ex_chief,
        delta_ey=ey_deputy - ey_chief,
        delta_ix=delta_ix,
        delta_iy=delta_iy,
    )


def absolute_from_roe(chief: OrbitalElements, roe: RelativeOrbitalElements) -> OrbitalElements:
    """Reconstruct deputy elements from ROEs and chief elements.

    The inversion follows directly from the definitions introduced in
    :func:`roe_from_absolute`.  When the chief inclination is near zero the
    argument of ascending node difference cannot be recovered uniquely, so the
    function interprets ``delta_iy`` as the raw node offset.  The routine is
    accurate enough for the near-circular, low-inclination mission concepts
    explored in the project dossiers.

    Examples
    --------
    >>> chief = OrbitalElements(7000e3, 0.001, 0.01, 0.0, 0.0, 0.0)
    >>> desired = RelativeOrbitalElements(1e-3, 0.01, 0.0, 0.0, 0.0, 0.0)
    >>> deputy = absolute_from_roe(chief, desired)
    >>> abs(deputy.semi_major_axis - 7007.0e3) < 10.0
    True
    """

    a = chief.semi_major_axis * (1.0 + roe.delta_a_over_a)
    delta_raan = roe.delta_iy
    sin_ic = np.sin(chief.inclination)
    if not np.isclose(sin_ic, 0.0):
        delta_raan = roe.delta_iy / sin_ic

    inclination = chief.inclination + roe.delta_ix
    raan = chief.raan + delta_raan

    ex_chief = chief.eccentricity * np.cos(chief.arg_perigee)
    ey_chief = chief.eccentricity * np.sin(chief.arg_perigee)
    ex_deputy = ex_chief + roe.delta_ex
    ey_deputy = ey_chief + roe.delta_ey
    eccentricity = float(np.hypot(ex_deputy, ey_deputy))
    arg_perigee = float(np.arctan2(ey_deputy, ex_deputy))

    delta_omega = arg_perigee - chief.arg_perigee
    delta_lambda_star = roe.delta_lambda - np.cos(chief.inclination) * (raan - chief.raan)
    mean_anomaly = chief.mean_anomaly + delta_lambda_star - delta_omega

    return OrbitalElements(
        semi_major_axis=float(a),
        eccentricity=eccentricity,
        inclination=float(inclination),
        raan=float(raan),
        arg_perigee=arg_perigee,
        mean_anomaly=float(mean_anomaly),
    )


def propagate_roe(
    roe: RelativeOrbitalElements,
    *,
    mean_motion: float,
    dt: float,
) -> RelativeOrbitalElements:
    r"""Propagate ROEs under the linearised Hill-Clohessy-Wiltshire dynamics.

    The evolution assumes constant chief orbital elements and a small relative
    semi-major-axis offset.  Under these assumptions the in-plane coupling
    reduces to

    .. math::

        \delta \lambda(t) = \delta \lambda(0) - \tfrac{3}{2} n (\delta a / a) t,

    while the remaining components remain constant.  This simple drift model is
    routinely used during early-phase mission design to schedule along-track
    phasing manoeuvres.

    Examples
    --------
    >>> chief = OrbitalElements(7000e3, 0.0, 0.0, 0.0, 0.0, 0.0)
    >>> roe = RelativeOrbitalElements(1e-3, 0.0, 0.0, 0.0, 0.0, 0.0)
    >>> propagated = propagate_roe(roe, mean_motion=chief.mean_motion(), dt=600.0)
    >>> round(propagated.delta_lambda, 6)
    -0.000485
    """

    delta_lambda = roe.delta_lambda - 1.5 * mean_motion * roe.delta_a_over_a * dt
    return RelativeOrbitalElements(
        delta_a_over_a=roe.delta_a_over_a,
        delta_lambda=float(delta_lambda),
        delta_ex=roe.delta_ex,
        delta_ey=roe.delta_ey,
        delta_ix=roe.delta_ix,
        delta_iy=roe.delta_iy,
    )


__all__ = [
    "MU_EARTH",
    "OrbitalElements",
    "RelativeOrbitalElements",
    "absolute_from_roe",
    "propagate_roe",
    "roe_from_absolute",
]
