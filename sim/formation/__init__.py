"""Formation-flying simulation helpers."""

from .design import design_j2_invariant_formation
from .triangle import simulate_triangle_formation

__all__ = [
    "design_j2_invariant_formation",
    "simulate_triangle_formation",
]

