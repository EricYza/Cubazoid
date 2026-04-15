from typing import List, Optional

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation
from matplotlib.colors import TABLEAU_COLORS

from .types import Placement


def placements_to_grid(n: int, placements: List[Placement]) -> np.ndarray:
    grid = np.full((n, n, n), fill_value=-1, dtype=int)
    for placement in placements:
        for x, y, z in placement.cells:
            grid[x, y, z] = placement.piece_id
    return grid


def visualize_solution(
    n: int,
    placements: List[Placement],
    interval: int = 1000,
    save_path: Optional[str] = None,
    show: bool = True,
):
    if placements is None:
        raise ValueError("No solution to visualize.")

    frames = []
    grid = np.full((n, n, n), fill_value=-1, dtype=int)
    frames.append(grid.copy())
    for placement in placements:
        for x, y, z in placement.cells:
            grid[x, y, z] = placement.piece_id
        frames.append(grid.copy())

    color_list = list(TABLEAU_COLORS.values())

    fig = plt.figure(figsize=(7, 7))
    ax = fig.add_subplot(111, projection="3d")

    def draw_frame(frame_idx: int):
        ax.clear()
        state = frames[frame_idx]
        filled = state != -1

        facecolors = np.empty(state.shape, dtype=object)
        facecolors[:] = "none"
        unique_ids = sorted(pid for pid in np.unique(state) if pid != -1)
        for pid in unique_ids:
            facecolors[state == pid] = color_list[pid % len(color_list)]

        if np.any(filled):
            ax.voxels(filled, facecolors=facecolors, edgecolor="black", linewidth=0.8)

        ax.set_xlim(0, n)
        ax.set_ylim(0, n)
        ax.set_zlim(0, n)
        ax.set_box_aspect((1, 1, 1))
        ax.set_title(f"3D Cube Construction: step {frame_idx}/{len(frames) - 1}")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.view_init(elev=25, azim=35)

    ani = animation.FuncAnimation(fig, draw_frame, frames=len(frames), interval=interval, repeat=False)

    if save_path:
        if save_path.lower().endswith(".gif"):
            ani.save(save_path, writer=animation.PillowWriter(fps=max(1, 1000 // interval)))
        else:
            ani.save(save_path, writer="ffmpeg", fps=max(1, 1000 // interval))

    if show:
        plt.show()
    else:
        plt.close(fig)

    return ani

