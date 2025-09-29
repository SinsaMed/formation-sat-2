r"""Geometric helpers for constellation safety assessments.

The routines in this module encapsulate geometric checks that appear
frequently in the constellation safety cases and proximity-operations
briefings.  They are intentionally lightweight so that analysts can evaluate
quick-look trades without launching full STK studies, while still maintaining
the conventions used in our mission documentation.
"""

from __future__ import annotations

import math
from typing import Iterable, Tuple

import numpy as np
from numpy.typing import ArrayLike, NDArray

Vector = NDArray[np.float64]


def triangle_side_lengths(vertices: Iterable[ArrayLike]) -> Tuple[float, float, float]:
    """Return the side lengths of a triangle defined by *vertices*.

    Parameters
    ----------
    vertices:
        An iterable with three three-dimensional vertices expressed in metres.

    Returns
    -------
    tuple of float
        Lengths of the triangle's sides ``(a, b, c)`` in metres.
    """

    pts = [np.asarray(v, dtype=float) for v in vertices]
    if len(pts) != 3:
        raise ValueError("Exactly three vertices are required to define a triangle.")
    a = np.linalg.norm(pts[1] - pts[2])
    b = np.linalg.norm(pts[0] - pts[2])
    c = np.linalg.norm(pts[0] - pts[1])
    return (a, b, c)


def triangle_area(vertices: Iterable[ArrayLike]) -> float:
    r"""Compute the area of a triangle in three-dimensional space.

    The area is obtained via the magnitude of the cross product between two
    edges, providing numerical stability for obtuse and acute configurations
    alike.  This matches the metric used in our STK engagement scripts when
    assessing separation buffers.

    Examples
    --------
    >>> import numpy as np
    >>> v = [np.array([0.0, 0.0, 0.0]),
    ...      np.array([1.0, 0.0, 0.0]),
    ...      np.array([0.0, 1.0, 0.0])]
    >>> triangle_area(v)
    0.5
    """

    pts = [np.asarray(v, dtype=float) for v in vertices]
    if len(pts) != 3:
        raise ValueError("Exactly three vertices are required to define a triangle.")
    edge1 = pts[1] - pts[0]
    edge2 = pts[2] - pts[0]
    return 0.5 * float(np.linalg.norm(np.cross(edge1, edge2)))


def triangle_aspect_ratio(vertices: Iterable[ArrayLike]) -> float:
    """Return the aspect ratio of a triangle.

    The aspect ratio is the longest edge divided by the shortest edge.  Values
    close to unity indicate nearly equilateral geometries, which typically yield
    better relative navigation observability in the mission simulations.
    """

    sides = triangle_side_lengths(vertices)
    shortest = min(sides)
    if math.isclose(shortest, 0.0):
        raise ValueError("Degenerate triangle with zero-length edge.")
    return max(sides) / shortest


def relative_position(reference: ArrayLike, follower: ArrayLike) -> Tuple[Vector, float]:
    """Compute the relative position vector and range between two spacecraft.

    Parameters
    ----------
    reference:
        Position of the reference spacecraft in an inertial frame.
    follower:
        Position of the follower spacecraft in the same frame.

    Returns
    -------
    tuple
        A tuple ``(delta, range)`` where ``delta`` is the follower-minus-reference
        vector in metres and ``range`` is its magnitude.
    """

    ref = np.asarray(reference, dtype=float)
    fol = np.asarray(follower, dtype=float)
    delta = fol - ref
    return delta, float(np.linalg.norm(delta))


def is_visible(
    observer: ArrayLike,
    target: ArrayLike,
    *,
    minimum_elevation_deg: float = 0.0,
    body_radius: float = 6_378_137.0,
) -> bool:
    r"""Return whether *target* is visible from *observer*.

    The check assumes both spacecraft are exterior to a spherical primary with
    radius ``body_radius`` (defaulting to WGS84 Earth's equatorial radius).  The
    line of sight is considered unobstructed when the elevation angle satisfies
    :math:`\sin(\text{el}) = -\hat{\boldsymbol{\rho}} \cdot \hat{\mathbf{r}} \geq
    \sin(\text{el}_\text{min})`, where ``el_min`` is specified by
    ``minimum_elevation_deg``.  This mirrors the condition used in the quick-look
    contact analysis notebooks that accompany the mission design reviews.

    Examples
    --------
    >>> is_visible([6778137.0, 0.0, 0.0], [6778137.0, 1000.0, 0.0])
    True
    >>> is_visible([6778137.0, 0.0, 0.0], [0.0, 6778137.0, 0.0])
    False
    """

    obs = np.asarray(observer, dtype=float)
    tgt = np.asarray(target, dtype=float)
    obs_norm = np.linalg.norm(obs)
    tgt_norm = np.linalg.norm(tgt)
    if obs_norm < body_radius or tgt_norm < body_radius:
        raise ValueError("Both spacecraft must be outside the primary body.")

    relative_vec = tgt - obs
    relative_norm = np.linalg.norm(relative_vec)
    if relative_norm == 0.0:
        return True

    # Check whether the line of sight intersects the primary body.
    direction_norm_sq = float(np.dot(relative_vec, relative_vec))
    projection = -float(np.dot(obs, relative_vec)) / direction_norm_sq
    if 0.0 <= projection <= 1.0:
        closest_point = obs + projection * relative_vec
        if np.linalg.norm(closest_point) <= body_radius:
            return False

    rho_hat = relative_vec / relative_norm
    r_hat = obs / obs_norm
    sine_elevation = -float(np.dot(rho_hat, r_hat))
    min_elevation_rad = math.radians(minimum_elevation_deg)
    return sine_elevation >= math.sin(min_elevation_rad)


__all__ = [
    "Vector",
    "is_visible",
    "relative_position",
    "triangle_area",
    "triangle_aspect_ratio",
    "triangle_side_lengths",
]
