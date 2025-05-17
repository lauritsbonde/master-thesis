import math
from typing import List, Tuple
from boats.boat import Boat
from alpha.rules import calculate_alpha

def create_v_formation(n: int) -> List[Boat]:
    spacing_x = .5
    spacing_y = 1.25
    positions: List[Tuple[float, float]] = []

    if n >= 1:
        positions.append((0, 0))  # Tip of the V (bottom center)
    if n >= 2:
        positions.append((-spacing_x, spacing_y))
    if n >= 3:
        positions.append((spacing_x, spacing_y))

    # Fill in additional boats outward and upward
    i = 3
    offset = 2
    while i < n:
        y = offset * spacing_y
        if i < n:
            positions.append((-offset * spacing_x, y))
            i += 1
        if i < n:
            positions.append((offset * spacing_x, y))
            i += 1
        offset += 1

    return create_boats_from_positions(positions)


def create_diagonal_line(n: int) -> List[Boat]:
    spacing_x = .5
    spacing_y = 1.25
    positions = [(i * spacing_x, i * spacing_y) for i in range(n)]
    return create_boats_from_positions(positions)


def create_line(n: int) -> List[Boat]:
    spacing_x = 0.5
    spacing_y = 1.25
    positions: List[Tuple[float, float]] = []

    for i in range(n):
        y = i * spacing_y

        if i % 2 == 0:
            x = 0.0  # center
        else:
            # alternate left/right for odd-indexed boats
            x = spacing_x if ((i // 2) % 2 == 0) else -spacing_x

        positions.append((x, y))

    return create_boats_from_positions(positions)

def create_single_boat(n: int) -> List[Boat]:
    if n < 1:
        return []
    return create_boats_from_positions([(0, 0)])


def create_boats_from_positions(positions: List[Tuple[float, float]]) -> List[Boat]:
    boats = [
        Boat(id=i, width=1, length=1, height=1, weight=10, speed=2, alpha=1.0, position=pos)
        for i, pos in enumerate(positions)
    ]

    all_positions = [b.position for b in boats]
    for boat in boats:
        boat.alpha = calculate_alpha(boat.position, [p for p in all_positions if p != boat.position])

    return boats
