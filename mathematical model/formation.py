import math
from typing import List, Tuple

class Shape:
    """
    Represents a 2D polygon shape.
    """
    def __init__(self, points: List[Tuple[float, float]]):
        self.points = points
        self.number_of_points = len(points)

# Define the ship shape (matches the C code)
SHIP_SHAPE = Shape([
    (0.0, 1.0),   # Top point (elongated)
    (0.5, 0.3),   # Top-right corner
    (0.5, -0.3),  # Bottom-right corner
    (0.0, -1.0),  # Bottom point (elongated)
    (-0.5, -0.3), # Bottom-left corner
    (-0.5, 0.3),  # Top-left corner
    (0.0, 1.0)    # Close the loop
])

def calculate_level(number_of_ships: int) -> int:
    """
    Calculates the maximum level of a pyramid given the number of ships.
    """
    return int((-1 + math.sqrt(1 + 8 * number_of_ships)) // 2)

def calculate_blocks_needed(level: int) -> int:
    """
    Calculates the number of ships needed to form a complete pyramid of a given level.
    """
    return level * (level + 1) // 2


def calculate_formation(number_of_ships: int, spacing: float = 1.25) -> List[Tuple[float, float]]:
    """
    Returns a list of (x, y) positions for ships in a pyramid-to-line formation.
    The formation transitions from a pyramid shape into a structured row formation.
    
    Args:
        number_of_ships (int): Total number of ships to position.
        spacing (float): Distance between ships.

    Returns:
        List[Tuple[float, float]]: List of (x, y) positions.
    """
    positions = []
    current_ship = 0
    pyramid_level = 0
    last_level_width = 0.0  # Width of the last pyramid level
    last_level_block_width = 0

    # Calculate pyramid structure
    pyramid_ships = calculate_level(number_of_ships)
    max_blocks = calculate_blocks_needed(pyramid_ships)

    # Build the pyramid formation
    while current_ship < number_of_ships:
        ships_in_level = pyramid_level + 1

        if current_ship > max_blocks:
            break  # Stop pyramid formation

        # Determine if remaining ships fit in this level
        if current_ship > number_of_ships:
            break  # Stop pyramid and transition to a line

        # Calculate x-offset to center-align the row
        x_offset = -0.5 * (ships_in_level - 1) * spacing

        for i in range(ships_in_level):
            positions.append((x_offset + i * spacing, -pyramid_level * spacing))
            current_ship += 1

        # Store width information for line transition
        last_level_width = (ships_in_level - 1) * spacing
        last_level_block_width = ships_in_level
        pyramid_level += 1

    # Calculate the starting x-position for the line
    line_start_x = -last_level_width * 0.5
    row_level = pyramid_level

    # Create rows that follow the pyramid formation width
    while current_ship < number_of_ships:
        ships_in_level = last_level_block_width

        if (row_level - pyramid_level) % 2 == 0:
            ships_in_level -= 1  # Reduce width every second row

        for i in range(min(ships_in_level, number_of_ships - current_ship)):
            x_shift = 0.6 if ships_in_level < last_level_block_width else 0.0
            positions.append(((line_start_x + x_shift) + i * spacing, -row_level * spacing))
            current_ship += 1

        row_level += 1

    return positions


# Print the formation positions
def print_formation(formation: List[Tuple[float, float]]):
    for i, (x, y) in enumerate(formation):
        print(f"Ship {i+1}: (x={x:.2f}, y={y:.2f})")