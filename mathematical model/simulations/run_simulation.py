from formations.elongated_hexagon import create_hexagon_formation
from formations.pyramid_to_line import create_pyramid_to_line
from formations.v_shape import create_v_shape
from formations.real_world import (
    create_v_formation,
    create_diagonal_line,
    create_line,
    create_single_boat,
    create_double,
)

from energy.power import calculatePowerUsage, calculateWhPerDistance, calculateTotalEnergyKWh
from utils.visualizer import plot_formation
from typing import Callable, List
from boats.boat import Boat
from config import SAILING_DISTANCE
from utils.validate_with_real_experiment import validate_with_real_experiment, find_double_speed, find_single_boat_speed
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
    formation_fn: Callable[..., List[Boat]],
    number_of_boats: int,
    distance: float,
    with_plot: bool,
    speed: float = 1.0,
) -> dict:
    boats = formation_fn(number_of_boats, speed=speed)

    power = calculatePowerUsage(boats)
    wh_per_meter = calculateWhPerDistance(boats, distance)
    kwh_used = calculateTotalEnergyKWh(boats, distance)

    plot_formation(boats, name, with_plot)

    return {
        "Formation": name,
        "Boats": number_of_boats,
        "Distance": distance,
        "Total Power (W)": power,
        "Power per Boat (W)": power / number_of_boats,
        "Wh per Meter": wh_per_meter,
        "Total Energy (kWh)": kwh_used,
    }

def run_simulation(with_plot: bool = False, export_csv: bool = True):
    os.makedirs("out", exist_ok=True)

    real_world_formations = {
        # "triangle": {
        #     "fn": create_v_formation,
        #     "boats": 3,
        #     "distance": SAILING_DISTANCE,
        # },
        # "diagonal-line": {
        #     "fn": create_diagonal_line,
        #     "boats": 3,
        #     "distance": SAILING_DISTANCE,
        # },
        # "offset-line": {
        #     "fn": create_line,
        #     "boats": 3,
        #     "distance": SAILING_DISTANCE,
        # },
        # "double": {
        #     "fn": create_double,
        #     "boats": 2,
        #     "distance": SAILING_DISTANCE,
        #     "speed": find_double_speed(),
        # },
        "singlerun": {
            "fn": create_single_boat,
            "boats": 1,
            "distance": SAILING_DISTANCE,
            "speed": find_single_boat_speed(),
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
                speed=cfg["speed"] if "speed" in cfg else 1.0,
            )
            results.append(result)
        return results

    real_world_results = run_batch(real_world_formations)
    validate_with_real_experiment(real_world_results)
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
