"""Unit tests for the constellation geometric helper routines."""

from __future__ import annotations

import math

import numpy as np
import pytest

from constellation import geometry


@pytest.fixture
def equilateral_vertices() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Provide vertices of a unit equilateral triangle in the orbital plane."""

    side = 1.0
    return (
        np.array([0.0, 0.0, 0.0]),
        np.array([side, 0.0, 0.0]),
        np.array([0.5 * side, math.sqrt(3) / 2 * side, 0.0]),
    )


def test_triangle_side_lengths_ordering(equilateral_vertices) -> None:
    """Side-length computation should be insensitive to vertex ordering."""

    lengths = geometry.triangle_side_lengths(equilateral_vertices)
    assert all(math.isclose(length, 1.0) for length in lengths)


def test_triangle_area_matches_expected(equilateral_vertices) -> None:
    """The area routine should agree with the analytical solution."""

    area = geometry.triangle_area(equilateral_vertices)
    assert math.isclose(area, math.sqrt(3) / 4)


def test_triangle_aspect_ratio_detects_degenerate_geometry() -> None:
    """A degenerate triangle should trigger a descriptive error."""

    vertices = (
        np.array([0.0, 0.0, 0.0]),
        np.array([0.0, 0.0, 0.0]),
        np.array([1.0, 0.0, 0.0]),
    )
    with pytest.raises(ValueError, match="Degenerate triangle"):
        geometry.triangle_aspect_ratio(vertices)


def test_relative_position_returns_vector_and_range() -> None:
    """Relative position should match manual subtraction."""

    reference = np.array([7_000_000.0, 0.0, 0.0])
    follower = np.array([7_010_000.0, -500.0, 250.0])
    delta, distance = geometry.relative_position(reference, follower)
    assert np.array_equal(delta, follower - reference)
    assert math.isclose(distance, np.linalg.norm(delta))


def test_is_visible_checks_body_intersection() -> None:
    """Visibility test should fail when the line of sight crosses Earth."""

    earth_radius = 6_378_137.0
    observer = np.array([earth_radius + 500e3, 0.0, 0.0])
    target = np.array([-(earth_radius + 500e3), 0.0, 0.0])
    assert not geometry.is_visible(observer, target)


def test_is_visible_validates_altitude() -> None:
    """Observers below the reference ellipsoid are not supported."""

    earth_radius = 6_378_137.0
    observer = np.array([earth_radius - 10.0, 0.0, 0.0])
    target = np.array([earth_radius + 500e3, 0.0, 0.0])
    with pytest.raises(ValueError, match="outside the primary body"):
        geometry.is_visible(observer, target)
