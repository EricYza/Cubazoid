import itertools
from typing import List, Tuple

import numpy as np

from .types import Coord


def normalize_coords(coords: List[Coord] | Tuple[Coord, ...]) -> Tuple[Coord, ...]:
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    zs = [c[2] for c in coords]
    minx, miny, minz = min(xs), min(ys), min(zs)
    shifted = sorted((x - minx, y - miny, z - minz) for x, y, z in coords)
    return tuple(shifted)


def tensor_to_coords(tensor: np.ndarray) -> Tuple[Coord, ...]:
    arr = np.asarray(tensor)
    if arr.ndim != 3:
        raise ValueError(f"Each shape tensor must be 3D, got shape {arr.shape}")
    coords = list(map(tuple, np.argwhere(arr > 0)))
    if not coords:
        raise ValueError("A shape tensor contains no occupied cubes.")
    return normalize_coords(coords)


def _generate_rotation_matrices() -> List[np.ndarray]:
    mats = []
    for perm in itertools.permutations(range(3)):
        p = np.zeros((3, 3), dtype=int)
        for i, j in enumerate(perm):
            p[i, j] = 1
        for signs in itertools.product([-1, 1], repeat=3):
            s = np.diag(signs)
            m = s @ p
            det = round(np.linalg.det(m))
            if det == 1:
                mats.append(m)

    unique = []
    seen = set()
    for m in mats:
        key = tuple(m.flatten())
        if key not in seen:
            seen.add(key)
            unique.append(m)
    if len(unique) != 24:
        raise RuntimeError(f"Expected 24 unique rotations, got {len(unique)}")
    return unique


ROTATION_MATRICES = _generate_rotation_matrices()


def rotate_coords(coords: Tuple[Coord, ...], rotation: np.ndarray) -> Tuple[Coord, ...]:
    pts = np.array(coords, dtype=int)
    rotated = (pts @ rotation.T).tolist()
    return normalize_coords([tuple(map(int, p)) for p in rotated])


def unique_orientations(coords: Tuple[Coord, ...]) -> List[Tuple[Coord, ...]]:
    seen = set()
    out = []
    for rotation in ROTATION_MATRICES:
        rot = rotate_coords(coords, rotation)
        if rot not in seen:
            seen.add(rot)
            out.append(rot)
    return out


def coords_to_tensor(coords: List[Coord] | Tuple[Coord, ...]) -> np.ndarray:
    coords = list(coords)
    maxx = max(c[0] for c in coords)
    maxy = max(c[1] for c in coords)
    maxz = max(c[2] for c in coords)
    arr = np.zeros((maxx + 1, maxy + 1, maxz + 1), dtype=np.uint8)
    for x, y, z in coords:
        arr[x, y, z] = 1
    return arr

