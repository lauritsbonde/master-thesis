from boats.boat import Boat
from alpha.rules import calculate_alpha

def create_v_shape(n: int) -> list[Boat]:
    spacing_x = 0.5
    spacing_y = 1.25
    center_index = n // 2

    # Step 1: Create boats with positions only
    boats = []
    for i in range(n):
        x = abs(i - center_index) * spacing_x
        y = abs(i - center_index) * spacing_y
        if i < center_index:
            x = -x
        position = (x + center_index * spacing_x, y)
        boats.append(Boat(id=i, width=1, length=1, height=1, weight=10, speed=2, alpha=1.0, position=position))

    # Step 2: Update alpha based on all positions
    positions = [b.position for b in boats]
    for boat in boats:
        boat.alpha = calculate_alpha(boat.position, [p for p in positions if p != boat.position])

    return boats
