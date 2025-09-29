"""Unit tests for the constellation reference-frame utilities."""

from __future__ import annotations

import numpy as np
import pytest
from numpy.testing import assert_allclose

from constellation import frames


@pytest.mark.parametrize(
    "position, velocity",
    [
        (np.array([7071e3, 7071e3, 0.0]), np.array([-5.0e3, 5.0e3, 0.0])),
        (np.array([0.0, -42164e3, 0.0]), np.array([3.07e3, 0.0, 0.0])),
    ],
)
def test_rotation_matrix_is_orthonormal(position: np.ndarray, velocity: np.ndarray) -> None:
    """The RTN rotation matrix must be orthonormal for representative states."""

    matrix = frames.rotation_matrix_eci_to_rtn(position, velocity)
    identity = matrix @ matrix.T
    assert_allclose(identity, np.eye(3), atol=1e-12)


def test_rtn_to_eci_is_inverse() -> None:
    """The RTN-to-ECI transform is the inverse of the forward mapping."""

    position = np.array([6_800_000.0, -120_000.0, 1_500_000.0])
    velocity = np.array([1_200.0, 7_500.0, -200.0])
    vector = np.array([100.0, -50.0, 25.0])

    forward = frames.eci_to_rtn(position, velocity, vector)
    recovered = frames.rtn_to_eci(position, velocity, forward)
    assert_allclose(recovered, vector, atol=1e-12)


def test_transform_vector_matches_manual_product() -> None:
    """``transform_vector`` should mirror a direct matrix multiplication."""

    matrix = np.array(
        [
            [0.0, 1.0, 0.0],
            [-1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0],
        ]
    )
    vector = np.array([2.0, 0.0, 3.0])
    expected = matrix @ vector
    assert_allclose(frames.transform_vector(vector, matrix), expected)


def test_rotation_matrix_raises_on_degenerate_state() -> None:
    """Zero-length position vectors are invalid for frame construction."""

    velocity = np.array([0.0, 7_500.0, 0.0])
    with pytest.raises(ValueError, match="zero-length vector"):
        frames.rotation_matrix_eci_to_rtn(np.zeros(3), velocity)
