from formations.elongated_hexagon import create_hexagon_formation
from formations.pyramid_to_line import create_pyramid_to_line
from formations.v_shape import create_v_shape
from formations.real_world import (
    create_v_formation,
    create_diagonal_line,
    create_line,
    create_single_boat,
)

from energy.power import calculatePowerUsage, calculateWhPerDistance
from utils.visualizer import plot_formation
from typing import Callable, List
from boats.boat import Boat
import csv
import os


def print_stats(boats: List[Boat], number_of_boats: int, distance: float):
    power = calculatePowerUsage(boats, efficency=0.8)
    wh_per_meter = calculateWhPerDistance(boats, distance)

    print(f"Total Power: {power:.2f} W")
    print(f"Power per boat: {power / number_of_boats:.2f} W")
    print(f"Wh per distance: {wh_per_meter:.4f} Wh/m")


def run_simulation_for_formation(
    name: str,
    formation_fn: Callable[[int], List[Boat]],
    number_of_boats: int,
    distance: float,
    with_plot: bool,
) -> dict:
    boats = formation_fn(number_of_boats)

    power = calculatePowerUsage(boats, efficency=0.8)
    wh_per_meter = calculateWhPerDistance(boats, distance)

    plot_formation(boats, name, with_plot)

    return {
        "Formation": name,
        "Boats": number_of_boats,
        "Distance": distance,
        "Total Power (W)": round(power, 2),
        "Power per Boat (W)": round(power / number_of_boats, 2),
        "Wh per Meter": round(wh_per_meter, 4),
    }

def run_simulation(with_plot: bool = False, export_csv: bool = True):
    os.makedirs("out", exist_ok=True)

    real_world_formations = {
        "triangle": {
            "fn": create_v_formation,
            "boats": 3,
            "distance": 80,
        },
        "diagonal-line": {
            "fn": create_diagonal_line,
            "boats": 3,
            "distance": 50,
        },
        "offset-line": {
            "fn": create_line,
            "boats": 3,
            "distance": 60,
        },
        "single-boat": {
            "fn": create_single_boat,
            "boats": 1,
            "distance": 20,
        },
    }

    generated_formations = {
            "elongated-hexagon": {
                "fn": create_hexagon_formation,
                "boats": 20,
                "distance": 100,
            },
            "pyramid-to-line": {
                "fn": create_pyramid_to_line,
                "boats": 20,
                "distance": 100,
            },
            "v-shape": {
                "fn": create_v_shape,
                "boats": 15,
                "distance": 90,
            },
        }

    def run_batch(name_config_map):
        results = []
        for name, cfg in name_config_map.items():
            result = run_simulation_for_formation(
                name=name,
                formation_fn=cfg["fn"],
                number_of_boats=cfg["boats"],
                distance=cfg["distance"],
                with_plot=with_plot,
            )
            results.append(result)
        return results

    real_world_results = run_batch(real_world_formations)
    generated_results = run_batch(generated_formations)

    # Export to CSV
    if export_csv:
        def save_csv(path, data):
            with open(path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)

        save_csv("out/real_world_results.csv", real_world_results)
        save_csv("out/generated_results.csv", generated_results)
        print("Saved CSVs to out/real_world_results.csv and out/generated_results.csv")
