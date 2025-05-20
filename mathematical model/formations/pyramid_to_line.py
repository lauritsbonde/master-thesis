import math
from typing import List, Tuple
from boats.boat import Boat
from alpha.rules import calculate_alpha


def calculate_blocks_needed(level: int) -> int:
    return level * (level + 1) // 2


def create_pyramid_to_line(n: int, speed: float = 1.0) -> List[Boat]:
    spacing = 1.25
    positions: List[Tuple[float, float]] = []

    current_ship = 0
    pyramid_level = 0
    last_level_width = 0.0
    last_level_block_width = 0

    # Heuristic: use log2(n) to limit pyramid size, not full triangle
    pyramid_ships = int(math.log2(n)) if n > 1 else 1
    max_blocks = calculate_blocks_needed(pyramid_ships)

    # Step 1: Build pyramid formation
    while current_ship < pyramid_ships:
        ships_in_level = pyramid_level + 1

        if current_ship > max_blocks:
            break  # Exit pyramid, go to line

        x_offset = -0.5 * (ships_in_level - 1) * spacing

        for i in range(ships_in_level):
            x = x_offset + i * spacing
            y = pyramid_level * spacing  # negative Y (top is front)
            positions.append((x, y))
            current_ship += 1
            if current_ship >= n:
                break

        last_level_width = (ships_in_level - 1) * spacing
        last_level_block_width = ships_in_level
        pyramid_level += 1

    # Step 2: Extend into rows under the pyramid
    line_start_x = -last_level_width * 0.5
    row_level = pyramid_level

    while current_ship < n:
        ships_in_level = last_level_block_width
        if (row_level - pyramid_level) % 2 == 0:
            ships_in_level -= 1

        for i in range(ships_in_level):
            if current_ship >= n:
                break
            x_shift = 0.6 if ships_in_level < last_level_block_width else 0.0
            x = (line_start_x + x_shift) + i * spacing
            y = row_level * spacing
            positions.append((x, y))
            current_ship += 1

        row_level += 1

    # Step 3: Create boats
    boats = [
        Boat(id=i, width=1, length=1, height=1, weight=2, speed=speed, alpha=1.0, position=pos)
        for i, pos in enumerate(positions)
    ]

    # Step 4: Calculate alpha
    all_positions = [b.position for b in boats]
    for boat in boats:
        boat.alpha = calculate_alpha(boat.position, [p for p in all_positions if p != boat.position])

    return boats
