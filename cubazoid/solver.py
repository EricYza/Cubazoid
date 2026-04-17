import math
import time
import warnings
from collections import deque
from typing import Dict, List, Optional, Set, Tuple

import numpy as np

from .geometry import tensor_to_coords, unique_orientations
from .types import Coord, Placement, PlacementOption


class CubazoidSolver:
    def __init__(
        self,
        shape_tensors: List[np.ndarray],
        enable_memo: bool = True,
        allow_disconnected: bool = False,
    ):
        if not shape_tensors:
            raise ValueError("Input shape list is empty.")

        self.infeasible_reason: Optional[str] = None
        self.original_tensors = [np.asarray(t) for t in shape_tensors]
        self.pieces = [tensor_to_coords(t) for t in self.original_tensors]
        self.volumes = [len(p) for p in self.pieces]

        invalid_volume_piece_ids = [i for i, vol in enumerate(self.volumes) if vol < 3 or vol > 5]
        if invalid_volume_piece_ids:
            ids_str = ", ".join(str(i) for i in invalid_volume_piece_ids)
            self.infeasible_reason = (
                f"Piece cube counts must be within [3, 5], but invalid pieces are: {ids_str}."
            )

        disconnected_piece_ids = [i for i, piece in enumerate(self.pieces) if not self._is_piece_connected(piece)]
        if disconnected_piece_ids:
            ids_str = ", ".join(str(i) for i in disconnected_piece_ids)
            if allow_disconnected:
                warnings.warn(
                    "Detected non-connected piece(s): "
                    f"{ids_str}. Solver will still treat each tensor as one rigid component.",
                    UserWarning,
                )
            else:
                reason = f"Disconnected pieces are not allowed, invalid pieces are: {ids_str}."
                if self.infeasible_reason:
                    self.infeasible_reason = f"{self.infeasible_reason} {reason}"
                else:
                    self.infeasible_reason = reason

        total_volume = sum(self.volumes)
        n = round(total_volume ** (1 / 3))
        if n < 1 or n ** 3 != total_volume:
            reason = f"Total volume {total_volume} is not a perfect cube."
            if self.infeasible_reason:
                self.infeasible_reason = f"{self.infeasible_reason} {reason}"
            else:
                self.infeasible_reason = reason
        self.n = n
        self.total_volume = total_volume

        if self.infeasible_reason:
            self.orientations = {}
            self.piece_class_id = []
            self.num_piece_classes = 0
            self.piece_placements = {}
            self.piece_placement_masks = {}
            self.cover_index = {}
            self.unplaceable_on_empty = []
            self.order = []
            self.enable_memo = enable_memo
            self.failed_states = set()
            self.deadline = None
            self.timed_out = False
            return

        self.orientations: Dict[int, List[Tuple[Coord, ...]]] = {
            i: unique_orientations(piece) for i, piece in enumerate(self.pieces)
        }
        self.piece_class_id = self._build_piece_classes()
        self.num_piece_classes = max(self.piece_class_id) + 1 if self.piece_class_id else 0

        (
            self.piece_placements,
            self.piece_placement_masks,
            self.cover_index,
            self.unplaceable_on_empty,
        ) = self._precompute_placements()

        self.order = sorted(
            range(len(self.pieces)),
            key=lambda i: (len(self.piece_placements[i]), -self.volumes[i], -len(self.orientations[i]), i),
        )

        self.enable_memo = enable_memo
        self.failed_states: Set[Tuple[int, Tuple[int, ...]]] = set()
        self.deadline: Optional[float] = None
        self.timed_out = False

    @staticmethod
    def _is_piece_connected(piece: Tuple[Coord, ...]) -> bool:
        if not piece:
            return False

        piece_set = set(piece)
        q = deque([piece[0]])
        visited = {piece[0]}
        directions = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]

        while q:
            x, y, z = q.popleft()
            for dx, dy, dz in directions:
                nxt = (x + dx, y + dy, z + dz)
                if nxt in piece_set and nxt not in visited:
                    visited.add(nxt)
                    q.append(nxt)

        return len(visited) == len(piece_set)

    def _cell_to_bit_index(self, cell: Coord) -> int:
        x, y, z = cell
        return x * self.n * self.n + y * self.n + z

    def _cells_to_mask(self, cells: Tuple[Coord, ...]) -> int:
        mask = 0
        for cell in cells:
            mask |= 1 << self._cell_to_bit_index(cell)
        return mask

    def _start_timer(self, max_seconds: Optional[float]) -> None:
        self.timed_out = False
        if max_seconds is None or max_seconds <= 0:
            self.deadline = None
            return
        self.deadline = time.monotonic() + max_seconds

    def _check_timeout(self) -> bool:
        if self.deadline is None:
            return False
        if time.monotonic() < self.deadline:
            return False
        self.timed_out = True
        return True

    def solve(self, max_seconds: Optional[float] = None) -> Optional[List[Placement]]:
        self._start_timer(max_seconds)
        if self.infeasible_reason:
            return None
        if self.unplaceable_on_empty:
            return None
        occupied = np.full((self.n, self.n, self.n), fill_value=-1, dtype=int)
        occupied_mask = 0
        remaining = tuple(self.order)
        if not self._forward_check(occupied_mask, remaining):
            return None
        success, placements = self._backtrack(occupied, occupied_mask, remaining, [])
        return placements if success else None

    def _build_piece_classes(self) -> List[int]:
        shape_to_class: Dict[Tuple[Coord, ...], int] = {}
        classes = []
        next_class = 0
        for piece in self.pieces:
            if piece not in shape_to_class:
                shape_to_class[piece] = next_class
                next_class += 1
            classes.append(shape_to_class[piece])
        return classes

    def _precompute_placements(
        self,
    ) -> Tuple[
        Dict[int, List[PlacementOption]],
        Dict[int, List[int]],
        Dict[int, Dict[Coord, List[int]]],
        List[int],
    ]:
        piece_placements: Dict[int, List[PlacementOption]] = {}
        piece_placement_masks: Dict[int, List[int]] = {}
        cover_index: Dict[int, Dict[Coord, List[int]]] = {}
        unplaceable_on_empty = []

        for piece_id in range(len(self.pieces)):
            seen_cells: Dict[Tuple[Coord, ...], int] = {}
            for orientation_id, orient in enumerate(self.orientations[piece_id]):
                maxx = max(c[0] for c in orient)
                maxy = max(c[1] for c in orient)
                maxz = max(c[2] for c in orient)
                if maxx >= self.n or maxy >= self.n or maxz >= self.n:
                    continue

                for sx in range(self.n - maxx):
                    for sy in range(self.n - maxy):
                        for sz in range(self.n - maxz):
                            cells = tuple(sorted((x + sx, y + sy, z + sz) for x, y, z in orient))
                            if cells not in seen_cells:
                                seen_cells[cells] = orientation_id

            placements = [
                PlacementOption(orientation_id=oid, cells=cells)
                for cells, oid in sorted(seen_cells.items())
            ]
            piece_placements[piece_id] = placements
            piece_placement_masks[piece_id] = [self._cells_to_mask(option.cells) for option in placements]

            cov: Dict[Coord, List[int]] = {}
            for idx, option in enumerate(placements):
                for cell in option.cells:
                    cov.setdefault(cell, []).append(idx)
            cover_index[piece_id] = cov

            if not placements:
                unplaceable_on_empty.append(piece_id)

        return piece_placements, piece_placement_masks, cover_index, unplaceable_on_empty

    @staticmethod
    def _can_place_mask(occupied_mask: int, placement_mask: int) -> bool:
        return (occupied_mask & placement_mask) == 0

    def _place(self, occupied: np.ndarray, piece_id: int, cells: Tuple[Coord, ...]) -> None:
        for x, y, z in cells:
            occupied[x, y, z] = piece_id

    def _unplace(self, occupied: np.ndarray, cells: Tuple[Coord, ...]) -> None:
        for x, y, z in cells:
            occupied[x, y, z] = -1

    def _empty_component_sizes(self, occupied: np.ndarray) -> List[int]:
        visited = np.zeros_like(occupied, dtype=bool)
        sizes = []
        directions = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]

        for x in range(self.n):
            for y in range(self.n):
                for z in range(self.n):
                    if occupied[x, y, z] != -1 or visited[x, y, z]:
                        continue
                    q = deque([(x, y, z)])
                    visited[x, y, z] = True
                    size = 0
                    while q:
                        cx, cy, cz = q.popleft()
                        size += 1
                        for dx, dy, dz in directions:
                            nx, ny, nz = cx + dx, cy + dy, cz + dz
                            if 0 <= nx < self.n and 0 <= ny < self.n and 0 <= nz < self.n:
                                if occupied[nx, ny, nz] == -1 and not visited[nx, ny, nz]:
                                    visited[nx, ny, nz] = True
                                    q.append((nx, ny, nz))
                    sizes.append(size)
        return sizes

    def _prune_holes(self, occupied: np.ndarray, remaining_piece_ids: Tuple[int, ...]) -> bool:
        if not remaining_piece_ids:
            return False

        rem_vols = [self.volumes[i] for i in remaining_piece_ids]
        min_vol = min(rem_vols)
        g = rem_vols[0]
        for v in rem_vols[1:]:
            g = math.gcd(g, v)
        sorted_vols = sorted(rem_vols)
        small_sum = sorted_vols[0] + (sorted_vols[1] if len(sorted_vols) > 1 else 0)

        for comp_size in self._empty_component_sizes(occupied):
            if comp_size < min_vol:
                return True
            if comp_size < small_sum and comp_size % g != 0:
                return True
        return False

    def _remaining_class_counts(self, remaining_piece_ids: Tuple[int, ...]) -> Tuple[int, ...]:
        counts = [0] * self.num_piece_classes
        for piece_id in remaining_piece_ids:
            counts[self.piece_class_id[piece_id]] += 1
        return tuple(counts)

    def _state_key(self, occupied_mask: int, remaining_piece_ids: Tuple[int, ...]) -> Tuple[int, Tuple[int, ...]]:
        return occupied_mask, self._remaining_class_counts(remaining_piece_ids)

    def _has_any_valid_placement(self, occupied_mask: int, piece_id: int) -> bool:
        for option_idx, _option in enumerate(self.piece_placements[piece_id]):
            if self._can_place_mask(occupied_mask, self.piece_placement_masks[piece_id][option_idx]):
                return True
        return False

    def _forward_check(self, occupied_mask: int, remaining_piece_ids: Tuple[int, ...]) -> bool:
        if self._check_timeout():
            return False
        seen_classes = set()
        for piece_id in remaining_piece_ids:
            class_id = self.piece_class_id[piece_id]
            if class_id in seen_classes:
                continue
            seen_classes.add(class_id)
            if not self._has_any_valid_placement(occupied_mask, piece_id):
                return False
        return True

    def _moves_covering_cell(
        self,
        occupied_mask: int,
        remaining_piece_ids: Tuple[int, ...],
        cell: Coord,
    ) -> List[Tuple[int, int, int]]:
        moves: List[Tuple[int, int, int]] = []
        seen_classes = set()

        for idx_in_tuple, piece_id in enumerate(remaining_piece_ids):
            class_id = self.piece_class_id[piece_id]
            if class_id in seen_classes:
                continue
            seen_classes.add(class_id)

            for placement_idx in self.cover_index[piece_id].get(cell, []):
                if self._can_place_mask(occupied_mask, self.piece_placement_masks[piece_id][placement_idx]):
                    moves.append((idx_in_tuple, piece_id, placement_idx))

        return moves

    def _select_target_and_moves(
        self,
        occupied: np.ndarray,
        occupied_mask: int,
        remaining_piece_ids: Tuple[int, ...],
    ) -> Tuple[Optional[Coord], List[Tuple[int, int, int]]]:
        empty_locs = np.argwhere(occupied == -1)
        if len(empty_locs) == 0:
            return None, []

        best_cell: Optional[Coord] = None
        best_moves: List[Tuple[int, int, int]] = []
        best_count = float("inf")

        for loc in empty_locs:
            cell = (int(loc[0]), int(loc[1]), int(loc[2]))
            moves = self._moves_covering_cell(occupied_mask, remaining_piece_ids, cell)
            move_count = len(moves)
            if move_count == 0:
                return cell, []
            if move_count < best_count:
                best_count = move_count
                best_cell = cell
                best_moves = moves
                if best_count == 1:
                    break

        return best_cell, best_moves

    def _backtrack(
        self,
        occupied: np.ndarray,
        occupied_mask: int,
        remaining_piece_ids: Tuple[int, ...],
        placements: List[Placement],
    ) -> Tuple[bool, Optional[List[Placement]]]:
        if self._check_timeout():
            return False, None
        if not remaining_piece_ids:
            if np.all(occupied != -1):
                return True, placements.copy()
            return False, None

        if self.enable_memo:
            key = self._state_key(occupied_mask, remaining_piece_ids)
            if key in self.failed_states:
                return False, None

        _target, moves = self._select_target_and_moves(occupied, occupied_mask, remaining_piece_ids)
        if _target is None:
            return True, placements.copy()
        if not moves:
            if self.enable_memo:
                self.failed_states.add(self._state_key(occupied_mask, remaining_piece_ids))
            return False, None

        for idx_in_tuple, piece_id, placement_idx in moves:
            if self._check_timeout():
                return False, None
            option = self.piece_placements[piece_id][placement_idx]
            option_mask = self.piece_placement_masks[piece_id][placement_idx]
            next_remaining = remaining_piece_ids[:idx_in_tuple] + remaining_piece_ids[idx_in_tuple + 1 :]
            next_occupied_mask = occupied_mask | option_mask
            self._place(occupied, piece_id, option.cells)

            if not self._prune_holes(occupied, next_remaining) and self._forward_check(
                next_occupied_mask, next_remaining
            ):
                placements.append(
                    Placement(
                        piece_id=piece_id,
                        orientation_id=option.orientation_id,
                        cells=option.cells,
                    )
                )
                ok, result = self._backtrack(occupied, next_occupied_mask, next_remaining, placements)
                if ok:
                    return True, result
                placements.pop()

            self._unplace(occupied, option.cells)

        if self.enable_memo:
            self.failed_states.add(self._state_key(occupied_mask, remaining_piece_ids))
        return False, None


class _DLXNode:
    __slots__ = ("left", "right", "up", "down", "column", "row_id")

    def __init__(self, column=None, row_id: int = -1):
        self.left = self
        self.right = self
        self.up = self
        self.down = self
        self.column = column
        self.row_id = row_id


class _DLXColumn(_DLXNode):
    __slots__ = ("name", "size", "is_primary")

    def __init__(self, name: int, is_primary: bool = True):
        super().__init__(column=self, row_id=-1)
        self.name = name
        self.size = 0
        self.is_primary = is_primary


class ExactCoverCubazoidSolver(CubazoidSolver):
    """
    True DLX node-based solver with symmetry breaking by collapsing identical pieces.
    Primary columns: cube cells only.
    Additional piece usage constraints are tracked as per-shape-class remaining counts.
    """

    def solve(self, max_seconds: Optional[float] = None) -> Optional[List[Placement]]:
        self._start_timer(max_seconds)
        if self.infeasible_reason:
            return None
        if self.unplaceable_on_empty:
            return None
        return self._solve_with_dlx()

    def _cell_to_col(self, cell: Coord) -> int:
        x, y, z = cell
        return x * self.n * self.n + y * self.n + z

    def _build_piece_classes_data(
        self,
    ) -> Tuple[List[List[int]], List[int], List[List[PlacementOption]]]:
        class_piece_ids: List[List[int]] = [[] for _ in range(self.num_piece_classes)]
        class_counts = [0] * self.num_piece_classes
        class_placements: List[List[PlacementOption]] = [[] for _ in range(self.num_piece_classes)]

        for piece_id, class_id in enumerate(self.piece_class_id):
            class_piece_ids[class_id].append(piece_id)
            class_counts[class_id] += 1

        for class_id, piece_ids in enumerate(class_piece_ids):
            if piece_ids:
                rep_piece_id = piece_ids[0]
                class_placements[class_id] = self.piece_placements[rep_piece_id]

        return class_piece_ids, class_counts, class_placements

    @staticmethod
    def _append_column(root: _DLXColumn, col: _DLXColumn) -> None:
        col.right = root
        col.left = root.left
        root.left.right = col
        root.left = col

    @staticmethod
    def _append_node_to_column(col: _DLXColumn, node: _DLXNode) -> None:
        node.down = col
        node.up = col.up
        col.up.down = node
        col.up = node
        node.column = col
        col.size += 1

    def _build_dlx_structure(
        self,
        class_counts: List[int],
        class_placements: List[List[PlacementOption]],
    ) -> Tuple[_DLXColumn, List[_DLXColumn], List[int], List[PlacementOption]]:
        num_cell_cols = self.n ** 3
        root = _DLXColumn(name=-1, is_primary=False)
        root.left = root
        root.right = root

        cell_columns: List[_DLXColumn] = []
        for col_id in range(num_cell_cols):
            col = _DLXColumn(name=col_id, is_primary=True)
            self._append_column(root, col)
            cell_columns.append(col)

        row_class_ids: List[int] = []
        row_options: List[PlacementOption] = []

        for class_id, count in enumerate(class_counts):
            if count == 0:
                continue
            for option in class_placements[class_id]:
                row_id = len(row_class_ids)
                row_class_ids.append(class_id)
                row_options.append(option)

                first: Optional[_DLXNode] = None
                prev: Optional[_DLXNode] = None
                for cell in option.cells:
                    col = cell_columns[self._cell_to_col(cell)]
                    node = _DLXNode(column=col, row_id=row_id)
                    self._append_node_to_column(col, node)

                    if first is None:
                        first = node
                        prev = node
                    else:
                        node.left = prev
                        node.right = first
                        prev.right = node
                        first.left = node
                        prev = node

        return root, cell_columns, row_class_ids, row_options

    @staticmethod
    def _choose_column(root: _DLXColumn) -> Optional[_DLXColumn]:
        col = root.right
        if col is root:
            return None

        best = col
        cur = col.right
        while cur is not root:
            if cur.size < best.size:
                best = cur
                if best.size <= 1:
                    break
            cur = cur.right
        return best

    @staticmethod
    def _cover(
        col: _DLXColumn,
        active_cell_flags: List[bool],
        active_cell_count: List[int],
    ) -> None:
        col.right.left = col.left
        col.left.right = col.right
        if col.is_primary and active_cell_flags[col.name]:
            active_cell_flags[col.name] = False
            active_cell_count[0] -= 1

        row = col.down
        while row is not col:
            node = row.right
            while node is not row:
                node.down.up = node.up
                node.up.down = node.down
                node.column.size -= 1
                node = node.right
            row = row.down

    @staticmethod
    def _uncover(
        col: _DLXColumn,
        active_cell_flags: List[bool],
        active_cell_count: List[int],
    ) -> None:
        row = col.up
        while row is not col:
            node = row.left
            while node is not row:
                node.column.size += 1
                node.down.up = node
                node.up.down = node
                node = node.left
            row = row.up

        if col.is_primary and not active_cell_flags[col.name]:
            active_cell_flags[col.name] = True
            active_cell_count[0] += 1
        col.right.left = col
        col.left.right = col

    def _solve_with_dlx(self) -> Optional[List[Placement]]:
        class_piece_ids, class_counts, class_placements = self._build_piece_classes_data()
        class_volumes = [0] * self.num_piece_classes
        for class_id, piece_ids in enumerate(class_piece_ids):
            if piece_ids:
                class_volumes[class_id] = self.volumes[piece_ids[0]]

        root, _cell_columns, row_class_ids, row_options = self._build_dlx_structure(class_counts, class_placements)
        if not row_class_ids:
            return None

        col = root.right
        while col is not root:
            if col.size == 0:
                return None
            col = col.right

        remaining_class_counts = class_counts.copy()
        remaining_volume = [sum(class_counts[c] * class_volumes[c] for c in range(self.num_piece_classes))]
        active_cell_flags = [True] * (self.n ** 3)
        active_cell_count = [self.n ** 3]
        chosen_row_ids: List[int] = []

        def search(depth: int) -> bool:
            if self._check_timeout():
                return False
            target_col = self._choose_column(root)
            if target_col is None:
                return all(v == 0 for v in remaining_class_counts)
            if target_col.size == 0:
                return False

            row = target_col.down
            while row is not target_col:
                if self._check_timeout():
                    return False
                row_id = row.row_id
                class_id = row_class_ids[row_id]
                if remaining_class_counts[class_id] > 0:
                    remaining_class_counts[class_id] -= 1
                    remaining_volume[0] -= class_volumes[class_id]
                    chosen_row_ids.append(row_id)

                    covered_cols: List[_DLXColumn] = []
                    node = row
                    while True:
                        self._cover(node.column, active_cell_flags, active_cell_count)
                        covered_cols.append(node.column)
                        node = node.right
                        if node is row:
                            break

                    prune = active_cell_count[0] != remaining_volume[0]
                    if not prune and search(depth + 1):
                        return True

                    for col_node in reversed(covered_cols):
                        self._uncover(col_node, active_cell_flags, active_cell_count)
                    chosen_row_ids.pop()
                    remaining_volume[0] += class_volumes[class_id]
                    remaining_class_counts[class_id] += 1

                row = row.down

            return False

        if not search(0):
            return None

        class_next_piece_idx = [0] * self.num_piece_classes
        placements: List[Placement] = []
        for row_id in chosen_row_ids:
            class_id = row_class_ids[row_id]
            piece_id = class_piece_ids[class_id][class_next_piece_idx[class_id]]
            class_next_piece_idx[class_id] += 1
            option = row_options[row_id]
            placements.append(
                Placement(
                    piece_id=piece_id,
                    orientation_id=option.orientation_id,
                    cells=option.cells,
                )
            )

        return placements
