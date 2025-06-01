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
from collections import defaultdict
import csv
import os

def run_simulation_for_formation(
    name: str,
    formation_fn: Callable[..., List[Boat]],
    number_of_boats: int,
    distance: float,
    with_plot: bool,
    real_world: bool = False,
    speed: float = 1.0,
) -> dict:
    boats = formation_fn(number_of_boats, speed=speed)

    print()

    power = calculatePowerUsage(boats)
    wh_per_meter = calculateWhPerDistance(boats, distance, power)
    kwh_used = calculateTotalEnergyKWh(boats, distance, power)

    plot_formation(boats, name, with_plot, real_world)

    return {
        "Formation": name,
        "Boats": number_of_boats,
        "Distance": distance,
        "Total Power (W)": power,
        "Power per Boat (W)": power / number_of_boats,
        "Wh per Meter": wh_per_meter,
        "Total Energy (kWh)": kwh_used,
        "Speed (m/s)": speed,
    }

def run_simulation(with_plot: bool = False, export_csv: bool = True):
    os.makedirs("out", exist_ok=True)

    print("double speed", find_double_speed())

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
        "double": {
            "fn": create_double,
            "boats": 2,
            "distance": SAILING_DISTANCE,
            "speed": find_double_speed(),
        },
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
                "boats": 24,
                "distance": 100,
            },
            "pyramid-to-line": {
                "fn": create_pyramid_to_line,
                "boats": 24,
                "distance": 100,
            },
            "v-shape": {
                "fn": create_v_shape,
                "boats": 24,
                "distance": 100,
            },
        }

    def run_batch(name_config_map, real_world):
        results = []
        for name, cfg in name_config_map.items():
            result = run_simulation_for_formation(
                name=name,
                formation_fn=cfg["fn"],
                number_of_boats=cfg["boats"],
                distance=cfg["distance"],
                with_plot=with_plot,
                speed=cfg["speed"] if "speed" in cfg else 1.0,
                real_world=real_world,
            )
            results.append(result)
        return results

    real_world_results = run_batch(real_world_formations, True)
    validation = validate_with_real_experiment(real_world_results)

    grouped_real_usage = defaultdict(list)
    for row in validation["valid"] + validation["suspicious"]:
        key = row["key"]
        real_kwh = row.get("real_kwh")
        if real_kwh is None:
            continue
        if "singlerun" in key:
            grouped_real_usage["singlerun"].append(real_kwh)
        elif "double" in key:
            grouped_real_usage["double"].append(real_kwh)

    # Compute average real kWh per formation
    avg_real_usage = {
        formation: sum(values) / len(values)
        for formation, values in grouped_real_usage.items()
        if values
    }

    # Assign to each row in real_world_results
    for row in real_world_results:
        formation = row["Formation"]
        row["Real Energy (kWh)"] = avg_real_usage.get(formation, "")

    print("Valid results", len(validation["valid"]), "Suspicious results", len(validation["suspicious"]))
    generated_results = run_batch(generated_formations, False)

    # Export to CSV
    if export_csv:
        def save_csv(path, data):
            def format_row(row):
                return {
                    k: (
                        f"{v:.3e}" if isinstance(v, float) and abs(v) < 0.1 else
                        f"{v:.2f}" if isinstance(v, float) else
                        v
                    )
                    for k, v in row.items()
                }

            fieldnames = [
                "Formation",
                "Boats",
                "Distance",
                "Speed (m/s)",
                "Total Power (W)",
                "Power per Boat (W)",
                "Wh per Meter",
                "Total Energy (kWh)",
            ]

            if path == "out/real_world_results.csv":
                fieldnames.append("Real Energy (kWh)")

            with open(path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows([format_row(row) for row in data])

        save_csv("out/real_world_results.csv", real_world_results)
        save_csv("out/generated_results.csv", generated_results)
        print("Saved CSVs to out/real_world_results.csv and out/generated_results.csv")
