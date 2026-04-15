from dataclasses import dataclass
from typing import Tuple


Coord = Tuple[int, int, int]


@dataclass(frozen=True)
class Placement:
    piece_id: int
    orientation_id: int
    cells: Tuple[Coord, ...]


@dataclass(frozen=True)
class PlacementOption:
    orientation_id: int
    cells: Tuple[Coord, ...]

