from .api import solve_and_visualize
from .examples import (
    build_large_cube_search_cases,
    build_named_pieces,
    build_test_cases,
    example_failure_mixed_3_4_5,
    example_pieces_3x3x3_straight_trominoes,
    example_success_mixed_3_4_5,
    example_unsat,
)
from .geometry import (
    ROTATION_MATRICES,
    coords_to_tensor,
    normalize_coords,
    rotate_coords,
    tensor_to_coords,
    unique_orientations,
)
from .solver import CubazoidSolver, ExactCoverCubazoidSolver
from .types import Coord, Placement, PlacementOption
from .visualization import placements_to_grid, visualize_solution

__all__ = [
    "Coord",
    "Placement",
    "PlacementOption",
    "ROTATION_MATRICES",
    "normalize_coords",
    "tensor_to_coords",
    "rotate_coords",
    "unique_orientations",
    "coords_to_tensor",
    "CubazoidSolver",
    "ExactCoverCubazoidSolver",
    "placements_to_grid",
    "visualize_solution",
    "example_pieces_3x3x3_straight_trominoes",
    "example_unsat",
    "example_success_mixed_3_4_5",
    "example_failure_mixed_3_4_5",
    "build_named_pieces",
    "build_large_cube_search_cases",
    "build_test_cases",
    "solve_and_visualize",
]
