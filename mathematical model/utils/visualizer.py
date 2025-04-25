import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches as patches
from boats.boat import Boat, BOAT_SHAPE

def translate_shape(shape, dx, dy):
    return [(x + dx, y + dy) for x, y in shape]

def plot_formation(boats: list[Boat], title: str = "Boat Formation"):
    alphas = [boat.alpha for boat in boats]
    norm = plt.Normalize(min(alphas), max(alphas))
    cmap = cm.get_cmap("viridis")

    fig, ax = plt.subplots(figsize=(10, 8))

    for i, boat in enumerate(boats):
        color = cmap(norm(boat.alpha))
        shape = translate_shape(BOAT_SHAPE, *boat.position)
        polygon = patches.Polygon(shape, closed=True, facecolor=color, edgecolor='black')
        ax.add_patch(polygon)
        ax.text(boat.position[0], boat.position[1] + 0.4, str(i), ha='center', fontsize=9)

    # After drawing all polygons
    all_x = [boat.position[0] for boat in boats]
    all_y = [boat.position[1] for boat in boats]
    ax.set_xlim(min(all_x) - 1, max(all_x) + 1)
    ax.set_ylim(min(all_y) - 1, max(all_y) + 1)

    # Add colorbar
    sm = cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label("Alpha (Drag Reduction Factor)")

    ax.set_title(title)
    ax.set_xlabel("X Position")
    ax.set_ylabel("Y Position")
    ax.set_aspect('equal')
    ax.grid(True)
    ax.invert_yaxis()
    plt.show()
