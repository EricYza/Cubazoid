import argparse

from cubazoid import (
    ROTATION_MATRICES,
    Coord,
    CubazoidSolver,
    ExactCoverCubazoidSolver,
    Placement,
    PlacementOption,
    build_named_pieces,
    build_test_cases,
    coords_to_tensor,
    example_failure_mixed_3_4_5,
    example_pieces_3x3x3_straight_trominoes,
    example_success_mixed_3_4_5,
    example_unsat,
    normalize_coords,
    placements_to_grid,
    rotate_coords,
    solve_and_visualize,
    tensor_to_coords,
    unique_orientations,
    visualize_solution,
)

__all__ = [
    "Coord",
    "Placement",
    "PlacementOption",
    "ROTATION_MATRICES",
    "normalize_coords",
    "tensor_to_coords",
    "rotate_coords",
    "unique_orientations",
    "CubazoidSolver",
    "ExactCoverCubazoidSolver",
    "placements_to_grid",
    "visualize_solution",
    "coords_to_tensor",
    "example_pieces_3x3x3_straight_trominoes",
    "example_unsat",
    "example_success_mixed_3_4_5",
    "example_failure_mixed_3_4_5",
    "build_named_pieces",
    "build_test_cases",
    "solve_and_visualize",
]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cubazoid solver runner")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all predefined test cases.",
    )
    parser.add_argument(
        "--case",
        default="hard_4x4x4_mixed_4blocks",
        help="Run a single test case by name.",
    )
    parser.add_argument(
        "--list-cases",
        action="store_true",
        help="List all available test case names and exit.",
    )
    parser.add_argument(
        "--include-large",
        action="store_true",
        help="Include 5x5x5 / 6x6x6 / 7x7x7 large search cases.",
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Disable visualization window.",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=800,
        help="Animation frame interval in milliseconds.",
    )
    parser.add_argument(
        "--backend",
        choices=["mrv", "exact"],
        default="mrv",
        help="Solver backend: mrv (current heuristic backtracking) or exact (Algorithm X / DLX style).",
    )
    args = parser.parse_args()

    tests = build_test_cases(include_large_search_cases=args.include_large)
    if args.list_cases:
        print("Available test cases:")
        for name in tests:
            print(f"- {name}")
        raise SystemExit(0)

    if args.all:
        print("Running all test cases...")
        for case_name, pieces in tests.items():
            print(f"\n=== Running {case_name} ===")
            try:
                solve_and_visualize(
                    pieces,
                    save_path=None,
                    interval=args.interval,
                    show=not args.no_show,
                    backend=args.backend,
                )
            except ValueError as err:
                print(f"Rejected: {err}")
    else:
        case_name = args.case
        if case_name not in tests:
            available = ", ".join(tests.keys())
            raise SystemExit(f"Unknown test case '{case_name}'. Available: {available}")
        print(f"Running test case: {case_name}")
        pieces = tests[case_name]
        solve_and_visualize(
            pieces,
            save_path=None,
            interval=args.interval,
            show=not args.no_show,
            backend=args.backend,
        )
