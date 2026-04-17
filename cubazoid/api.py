from typing import List, Optional

import numpy as np

from .solver import CubazoidSolver, ExactCoverCubazoidSolver
from .types import Placement
from .visualization import visualize_solution


def solve_and_visualize(
    shape_tensors: List[np.ndarray],
    save_path: Optional[str] = None,
    interval: int = 900,
    show: bool = True,
    backend: str = "mrv",
    timeout_sec: Optional[float] = None,
) -> Optional[List[Placement]]:
    if backend == "mrv":
        solver = CubazoidSolver(shape_tensors)
    elif backend == "exact":
        solver = ExactCoverCubazoidSolver(shape_tensors)
    else:
        raise ValueError(f"Unknown backend '{backend}'. Supported: mrv, exact")

    placements = solver.solve(max_seconds=timeout_sec)
    if placements is None:
        if solver.timed_out:
            if timeout_sec is None or timeout_sec <= 0:
                print("Search timed out.")
            else:
                print(f"Search timed out after {timeout_sec:.3f} seconds.")
        print("No cube-forming configuration exists.")
        return None

    print(f"Solved[{backend}]: {len(placements)} pieces fill a {solver.n}x{solver.n}x{solver.n} cube.")
    for step, placement in enumerate(placements, start=1):
        print(
            f"Step {step}: piece={placement.piece_id}, "
            f"orientation={placement.orientation_id}, cells={placement.cells}"
        )

    if show or save_path:
        visualize_solution(solver.n, placements, interval=interval, save_path=save_path, show=show)
    return placements
