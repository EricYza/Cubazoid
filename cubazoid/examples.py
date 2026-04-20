from typing import Dict, List

import numpy as np

from .geometry import coords_to_tensor


def example_pieces_3x3x3_straight_trominoes() -> List[np.ndarray]:
    tromino = coords_to_tensor([(0, 0, 0), (1, 0, 0), (2, 0, 0)])
    return [tromino.copy() for _ in range(9)]


def example_unsat() -> List[np.ndarray]:
    a = coords_to_tensor([(0, 0, 0), (1, 0, 0), (0, 1, 0)])
    b = coords_to_tensor([(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)])
    c = coords_to_tensor([(0, 0, 0), (1, 0, 0), (2, 0, 0), (0, 1, 0)])
    return [a, b, c]


def example_success_mixed_3_4_5() -> List[np.ndarray]:
    pieces = [
        coords_to_tensor([(0, 0, 0), (1, 0, 0), (2, 0, 0)]),
        coords_to_tensor([(2, 1, 0), (1, 1, 0), (0, 1, 0), (0, 2, 0)]),
        coords_to_tensor([(1, 2, 0), (2, 2, 0), (2, 2, 1), (1, 2, 1), (0, 2, 1)]),
        coords_to_tensor([(0, 1, 1), (1, 1, 1), (2, 1, 1), (2, 0, 1), (1, 0, 1)]),
        coords_to_tensor([(0, 0, 1), (0, 0, 2), (1, 0, 2), (2, 0, 2), (2, 1, 2)]),
        coords_to_tensor([(1, 1, 2), (0, 1, 2), (0, 2, 2), (1, 2, 2), (2, 2, 2)]),
    ]
    return pieces


def example_failure_mixed_3_4_5() -> List[np.ndarray]:
    pieces = [
        coords_to_tensor([(0, 0, 0), (1, 0, 0), (0, 1, 0)]),
        coords_to_tensor([(0, 0, 0), (1, 0, 0), (2, 0, 0), (1, 1, 0)]),
        coords_to_tensor([(0, 0, 0), (1, 0, 0), (2, 0, 0), (3, 0, 0), (4, 0, 0)]),
        coords_to_tensor([(0, 0, 0), (1, 0, 0), (2, 0, 0), (3, 0, 0), (0, 1, 0)]),
        coords_to_tensor([(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0), (0, 0, 1)]),
        coords_to_tensor([(0, 0, 0), (1, 0, 0), (2, 0, 0), (1, 1, 0), (1, 0, 1)]),
    ]
    return pieces


def build_named_pieces() -> Dict[str, np.ndarray]:
    i3 = coords_to_tensor([(0, 0, 0), (1, 0, 0), (2, 0, 0)])
    l3 = coords_to_tensor([(0, 0, 0), (1, 0, 0), (0, 1, 0)])

    i4 = coords_to_tensor([(0, 0, 0), (1, 0, 0), (2, 0, 0), (3, 0, 0)])
    o4 = coords_to_tensor([(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0)])
    l4 = coords_to_tensor([(0, 0, 0), (1, 0, 0), (2, 0, 0), (0, 1, 0)])
    t4 = coords_to_tensor([(0, 0, 0), (1, 0, 0), (2, 0, 0), (1, 1, 0)])
    s4 = coords_to_tensor([(0, 0, 0), (1, 0, 0), (1, 1, 0), (2, 1, 0)])
    pillar4 = coords_to_tensor([(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1)])

    i5 = coords_to_tensor([(0, 0, 0), (1, 0, 0), (2, 0, 0), (3, 0, 0), (4, 0, 0)])
    l5 = coords_to_tensor([(0, 0, 0), (1, 0, 0), (2, 0, 0), (3, 0, 0), (0, 1, 0)])
    t5 = coords_to_tensor([(0, 0, 0), (1, 0, 0), (2, 0, 0), (1, 1, 0), (1, 0, 1)])
    p5 = coords_to_tensor([(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0), (0, 0, 1)])
    u5 = coords_to_tensor([(0, 0, 0), (1, 0, 0), (2, 0, 0), (0, 1, 0), (2, 1, 0)])
    weird5 = coords_to_tensor([(0, 0, 0), (1, 0, 0), (2, 0, 0), (0, 1, 0), (2, 0, 1)])

    return {
        "I3": i3,
        "L3": l3,
        "I4": i4,
        "O4": o4,
        "L4": l4,
        "T4": t4,
        "S4": s4,
        "Pillar4": pillar4,
        "I5": i5,
        "L5": l5,
        "T5": t5,
        "P5": p5,
        "U5": u5,
        "Weird5": weird5,
    }


def _expand_piece_counts(pieces: Dict[str, np.ndarray], counts: Dict[str, int]) -> List[np.ndarray]:
    out: List[np.ndarray] = []
    for name, count in counts.items():
        out.extend(pieces[name].copy() for _ in range(count))
    return out


def build_large_cube_search_cases() -> Dict[str, List[np.ndarray]]:
    """
    Large search cases for 5x5x5 / 6x6x6 / 7x7x7.
    All cases satisfy:
    1) Total volume is exactly n^3.
    2) Every piece is size 3~5 and can be placed in the target cube at least on empty board.
    So these will not be rejected by front checks and will enter search.
    """
    p = build_named_pieces()
    return {
        # 3*3 + 4*5 + 5*18 = 125
        "search_5x5x5_mixed_balanced_a": _expand_piece_counts(
            p,
            {
                "I3": 3,
                "L3": 2,
                "I4": 1,
                "O4": 1,
                "L4": 1,
                "T4": 1,
                "S4": 1,
                "I5": 4,
                "L5": 5,
                "T5": 4,
                "P5": 5,
            },
        ),
        # 3*4 + 4*2 + 5*21 = 125
        "search_5x5x5_mixed_balanced_b": _expand_piece_counts(
            p,
            {
                "I3": 2,
                "L3": 2,
                "L4": 1,
                "T4": 1,
                "I5": 5,
                "L5": 6,
                "T5": 5,
                "P5": 5,
            },
        ),
        # 3*12 + 4*15 + 5*24 = 216
        "search_6x6x6_mixed_balanced": _expand_piece_counts(
            p,
            {
                "I3": 6,
                "L3": 6,
                "I4": 3,
                "O4": 3,
                "L4": 3,
                "T4": 2,
                "S4": 2,
                "Pillar4": 2,
                "I5": 6,
                "L5": 6,
                "T5": 6,
                "P5": 6,
            },
        ),
        # 3*6 + 4*20 + 5*49 = 343
        "search_7x7x7_mixed_balanced": _expand_piece_counts(
            p,
            {
                "I3": 1,
                "L3": 5,
                "I4": 2,
                "O4": 4,
                "L4": 4,
                "T4": 4,
                "S4": 4,
                "Pillar4": 2,
                "I5": 2,
                "L5": 11,
                "T5": 8,
                "U5": 7,
                "P5": 10,
                "Weird5": 11,
            },
        ),
    }


def build_test_cases(include_large_search_cases: bool = False) -> Dict[str, List[np.ndarray]]:
    p = build_named_pieces()
    cases = {
        "easy_3x3x3_all_I3": [p["I3"].copy() for _ in range(9)],
        "easy_2x2x2_two_4blocks": [p["O4"].copy(), p["Pillar4"].copy()],
        "medium_3x3x3_mixed": [
            p["I3"].copy(),
            p["I3"].copy(),
            p["L3"].copy(),
            p["L3"].copy(),
            p["I3"].copy(),
            p["O4"].copy(),
            p["L4"].copy(),
            p["T4"].copy(),
        ],
        "hard_4x4x4_all_I4": [p["I4"].copy() for _ in range(16)],
        "success_mixed_3_4_5": example_success_mixed_3_4_5(),
        "failure_mixed_3_4_5": example_failure_mixed_3_4_5(),
        "hard_4x4x4_mixed_4blocks": [
            p["I4"].copy(),
            p["I4"].copy(),
            p["I4"].copy(),
            p["I4"].copy(),
            p["O4"].copy(),
            p["O4"].copy(),
            p["O4"].copy(),
            p["O4"].copy(),
            p["L4"].copy(),
            p["L4"].copy(),
            p["T4"].copy(),
            p["T4"].copy(),
            p["S4"].copy(),
            p["S4"].copy(),
            p["Pillar4"].copy(),
            p["Pillar4"].copy(),
        ],
        "hard_4x4x4_mixed_3_5_fail": [
            p["I5"].copy(),
            p["L5"].copy(),
            p["P5"].copy(),
            p["T5"].copy(),
            p["I5"].copy(),
            p["L5"].copy(),
            p["P5"].copy(),
            p["T5"].copy(),
            p["I3"].copy(),
            p["I3"].copy(),
            p["L3"].copy(),
            p["L3"].copy(),
            p["I3"].copy(),
            p["I3"].copy(),
            p["L3"].copy(),
            p["L3"].copy(),
        ],
        "reject_not_perfect_cube": [p["T4"].copy() for _ in range(6)],
        # Volume is 27 (3x3x3), but one piece is disconnected and should be rejected by strict input checks.
        "reject_disconnected_piece_3x3x3": [
            coords_to_tensor([(0, 0, 0), (0, 1, 0), (2, 0, 0)]),
            p["I3"].copy(),
            p["I3"].copy(),
            p["I3"].copy(),
            p["I3"].copy(),
            p["I3"].copy(),
            p["I3"].copy(),
            p["I3"].copy(),
            p["I3"].copy(),
        ],
    }
    if include_large_search_cases:
        cases.update(build_large_cube_search_cases())
    return cases
