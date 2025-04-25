from typing import List, Tuple
from boats.boat import Boat
from alpha.rules import calculate_alpha


def calculate_blocks_needed(level: int) -> int:
    return level * (level + 1) // 2


def create_hexagon_formation(n: int) -> List[Boat]:
    spacing = 1.25
    positions: List[Tuple[float, float]] = []

    current_ship = 0
    top_level = 0
    last_row_width = 0

    # Step 1: Estimate top pyramid size
    # We use a heuristic: divide n into 3 parts (top, middle, bottom)
    estimated_top_levels = 1
    while calculate_blocks_needed(estimated_top_levels + 1) <= n // 3:
        estimated_top_levels += 1

    # Step 2: Build top pyramid
    for level in range(estimated_top_levels):
        ships_in_level = level + 1
        x_offset = -0.5 * (ships_in_level - 1) * spacing
        y = -level * spacing  # top goes upwards (negative y)

        for i in range(ships_in_level):
            if current_ship >= n:
                break
            x = x_offset + i * spacing
            positions.append((x, y))
            current_ship += 1

        last_row_width = ships_in_level
        top_level = level

    # Step 3: Middle section (same width as top's last row)
    middle_rows = max(1, n // 6)  # tweak how long the center is
    for row in range(middle_rows):
        x_offset = -0.5 * (last_row_width - 1) * spacing
        y = -(top_level + 1 + row) * spacing

        for i in range(last_row_width):
            if current_ship >= n:
                break
            x = x_offset + i * spacing
            positions.append((x, y))
            current_ship += 1

    # Step 4: Bottom pyramid (reversed)
    bottom_level = 1
    while current_ship < n:
        ships_in_level = last_row_width - bottom_level
        if ships_in_level <= 0:
            break

        x_offset = -0.5 * (ships_in_level - 1) * spacing
        y = -(top_level + middle_rows + bottom_level) * spacing

        for i in range(ships_in_level):
            if current_ship >= n:
                break
            x = x_offset + i * spacing
            positions.append((x, y))
            current_ship += 1

        bottom_level += 1

    # Create boats
    boats = [
        Boat(id=i, width=1, length=1, height=1, weight=10, speed=2, alpha=1.0, position=pos)
        for i, pos in enumerate(positions)
    ]

    # Compute alphas
    all_positions = [b.position for b in boats]
    for boat in boats:
        boat.alpha = calculate_alpha(boat.position, [p for p in all_positions if p != boat.position])

    return boats
