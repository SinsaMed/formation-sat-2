"""Linear-Quadratic Regulator utilities for formation station-keeping."""

from __future__ import annotations

from functools import lru_cache
from typing import Optional

import numpy as np
from numpy.typing import ArrayLike
from scipy.linalg import solve_continuous_are

Vector = np.ndarray


def _build_state_matrices(mean_motion: float) -> tuple[np.ndarray, np.ndarray]:
    """Construct the HCW state-space matrices for the given mean motion."""

    n = float(mean_motion)
    a_matrix = np.array(
        [
            [0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
            [3.0 * n**2, 0.0, 0.0, 0.0, 2.0 * n, 0.0],
            [0.0, 0.0, 0.0, -2.0 * n, 0.0, 0.0],
            [0.0, 0.0, -n**2, 0.0, 0.0, 0.0],
        ],
        dtype=float,
    )
    b_matrix = np.array(
        [
            [0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=float,
    )
    return a_matrix, b_matrix


@lru_cache(maxsize=16)
def _cached_gain(mean_motion: float, q_bytes: bytes | None, r_bytes: bytes | None) -> np.ndarray:
    """Cached helper resolving the continuous-time Riccati equation."""

    q_matrix = np.frombuffer(q_bytes, dtype=float).reshape((6, 6)) if q_bytes else np.eye(6)
    r_matrix = np.frombuffer(r_bytes, dtype=float).reshape((3, 3)) if r_bytes else np.eye(3)
    a_matrix, b_matrix = _build_state_matrices(mean_motion)
    riccati = solve_continuous_are(a_matrix, b_matrix, q_matrix, r_matrix)
    gain = np.linalg.solve(r_matrix, b_matrix.T @ riccati)
    return gain


def compute_lqr_gain(
    mean_motion: float,
    q_matrix: Optional[ArrayLike] = None,
    r_matrix: Optional[ArrayLike] = None,
) -> np.ndarray:
    """Return the optimal continuous-time LQR gain matrix for the HCW model."""

    q = np.eye(6) if q_matrix is None else np.ascontiguousarray(q_matrix, dtype=float)
    r = np.eye(3) if r_matrix is None else np.ascontiguousarray(r_matrix, dtype=float)
    if q.shape != (6, 6):
        raise ValueError("Q matrix must be 6x6 for the HCW state model.")
    if r.shape != (3, 3):
        raise ValueError("R matrix must be 3x3 for the HCW control inputs.")

    q_bytes = q.tobytes() if q_matrix is not None else None
    r_bytes = r.tobytes() if r_matrix is not None else None
    return _cached_gain(float(mean_motion), q_bytes, r_bytes)


def compute_lqr_delta_v(
    relative_state: ArrayLike,
    mean_motion: float,
    burn_duration_s: float,
    *,
    q_matrix: Optional[ArrayLike] = None,
    r_matrix: Optional[ArrayLike] = None,
) -> Vector:
    """Compute the optimal delta-V in LVLH coordinates using the LQR law."""

    state = np.ascontiguousarray(relative_state, dtype=float).ravel()
    if state.size != 6:
        raise ValueError("Relative state must contain six elements.")
    gain = compute_lqr_gain(mean_motion, q_matrix=q_matrix, r_matrix=r_matrix)
    control_acceleration = -gain @ state
    delta_v = control_acceleration * float(burn_duration_s)
    return delta_v.astype(float, copy=False)
