from constants import DATA_DIR, OUT_DIR
from boat_log_parser import parse_boat_file
from pathlib import Path
from processer import process_run
from visualize import (
  extract_singlerun_grouped,
  extract_speed_by_config,
  extract_power_by_config,
  plot_singlerun_power_and_speed,
  plot_power_and_speed_comparison_by_boat,
)

import os
import json

if __name__ == "__main__":
    data_dir = Path(DATA_DIR)
    files = list(data_dir.glob("*.txt"))

    all_runs_by_file = {}

    for file in files:
        print(f"Parsing {file.name}")
        runs = parse_boat_file(file)
        all_runs_by_file[file.stem] = runs

    for run_key, run_list in all_runs_by_file.items():
        print(f"Processing file: {run_key}")
        for run in run_list:
            try:
                result = process_run(run)
                run.update(result)
            except ValueError as e:
                print(f"Error processing run: {e}")

    # Visualize
    # Single run boxplot
    speeds = extract_singlerun_grouped(all_runs_by_file, key="speed")
    powers = extract_singlerun_grouped(all_runs_by_file, key="power_consumption")
    plot_singlerun_power_and_speed(speeds, powers, output_name="singleruns_power_speed")

    # Single boat comparison (dual y-axis)
    power_data = extract_power_by_config(all_runs_by_file, boats=[1, 3])
    speed_data = extract_speed_by_config(all_runs_by_file, boats=[1, 3])
    plot_power_and_speed_comparison_by_boat(power_data, speed_data, save_as="power_speed_by_boat")

    # Write to JSON
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = f"{OUT_DIR}/processed_boat_data.json"
    with open(out_path, "w") as f:
        json.dump(all_runs_by_file, f, indent=2)
