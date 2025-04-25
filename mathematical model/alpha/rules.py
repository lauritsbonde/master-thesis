def calculate_alpha(position: tuple[float, float], neighbors: list[tuple[float, float]]) -> float:
    if not neighbors:
        return 1.0

    x, y = position

    front_influence = 0.0
    side_influence = 0.0

    for nx, ny in neighbors:
        dx = nx - x
        dy = ny - y

        distance = (dx**2 + dy**2) ** 0.5
        if distance == 0:
            continue

        angle = abs(dx / distance)

        # dy > 0 means the neighbor is behind this boat
        if dy < 0:
            if angle < 0.5:  # Mostly directly behind
                front_influence += 1 / distance
            else:
                side_influence += 0.5 / distance

    raw_alpha = 1.0 - (0.2 * front_influence + 0.1 * side_influence)
    return max(0.5, min(raw_alpha, 1.0))
