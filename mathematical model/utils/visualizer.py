import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches as patches
import numpy as np
import matplotlib.colors as mcolors
import os
from boats.boat import Boat, BOAT_SHAPE

def translate_shape(shape, dx, dy):
    return [(x + dx, y + dy) for x, y in shape]

def plot_formation(boats: list[Boat], title: str = "Boat Formation", show_plot: bool = True):
    alphas = [boat.alpha for boat in boats]
    norm = plt.Normalize(min(alphas), max(alphas))
    base_cmap = cm.get_cmap("viridis", 256)

    # Create a new cmap with fixed alpha added
    alpha = 0.25
    colors = base_cmap(np.linspace(0, 1, 256))
    colors[:, 3] = alpha  # replace alpha channel

    # Make a new ListedColormap
    cmap_with_alpha = mcolors.ListedColormap(colors)

    # Now use this for both shapes and colorbar
    cmap = cmap_with_alpha

    fig, ax = plt.subplots(figsize=(10, 8))

    for i, boat in enumerate(boats):
        color = (*cmap(norm(boat.alpha))[:3], 0.25)
        shape = translate_shape(BOAT_SHAPE, *boat.position)
        polygon = patches.Polygon(shape, closed=True, facecolor=color, edgecolor='black')
        ax.add_patch(polygon)
        ax.text(boat.position[0], boat.position[1] - 0.4, f"ID: {i}", ha='center', fontsize=9)
        ax.text(boat.position[0], boat.position[1] + 0.4, f"Alpha: {boat.alpha:.2f}", ha='center', fontsize=9)

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

    # save the plot
    save_path = f"plots/{title.replace(' ', '_').lower()}.png"
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, bbox_inches="tight", dpi=300)
    print(f"Saved plot to {save_path}")

    if show_plot:
        plt.show()
    else:
        plt.close(fig)
