from constants import DATA_DIR, OUT_DIR
from boat_log_parser import parse_boat_file
from boat_formation_parser import parse_group_run_file
from pathlib import Path
from processer import process_run
from visualize import (
    extract_singlerun_grouped,
    extract_speed_by_config,
    extract_power_by_config,
    extract_formation_data,
    plot_singlerun_power_and_speed,
    plot_power_and_speed_comparison_by_boat,
    plot_formation_comparison,
)

import os
import json

if __name__ == "__main__":
    data_dir = Path(DATA_DIR)
    all_runs_by_file = {}

    for sub_dir in data_dir.iterdir():
        if not sub_dir.is_dir():
          continue

        date_label = sub_dir.name
        files = list(sub_dir.glob("*.txt"))
        print(f"Found {len(files)} files in {sub_dir}")

        for file in files:
            try:
                runs = []
                if "diagonal" in file.name or "offset line" in file.name or "triangle" in file.name:
                    runs = parse_group_run_file(file)
                else:
                    runs = parse_boat_file(file)

                for run in runs:
                    run["date"] = date_label

                # Group by filename only (no folder), and accumulate runs
                key = file.stem
                all_runs_by_file.setdefault(key, []).extend(runs)

            except Exception as e:
                print(f"Failed to parse {file}: {e}")

    # Process all runs after collecting
    for run_key, run_list in all_runs_by_file.items():
        for run in run_list:
            try:
                result = process_run(run)
                run.update(result)
            except ValueError as e:
                print(f"Error processing run: {e}")

    # Visualize
    speeds = extract_singlerun_grouped(all_runs_by_file, key="speed")
    powers = extract_singlerun_grouped(all_runs_by_file, key="power_consumption_kwh")
    plot_singlerun_power_and_speed(speeds, powers, output_name="singleruns_power_speed")

    power_data = extract_power_by_config(all_runs_by_file, boats=[1, 3])
    speed_data = extract_speed_by_config(all_runs_by_file, boats=[1, 3])
    plot_power_and_speed_comparison_by_boat(power_data, speed_data, save_as="power_speed_by_boat_double")

    # Existing extraction for formations
    formations = ["diagonal", "offset line", "triangle"]
    formation_speeds, formation_powers = extract_formation_data(all_runs_by_file, formations)

    # Existing singlerun extraction
    singlerun_speeds = extract_singlerun_grouped(all_runs_by_file, key="speed")
    singlerun_powers = extract_singlerun_grouped(all_runs_by_file, key="power_consumption_kwh")

    # Only include Boat 1 and 3
    relevant_singleruns = {
        k: v for k, v in singlerun_speeds.items() if k in ["boat_1_singlerun", "boat_3_singlerun"]
    }
    relevant_singlerun_powers = {
        k: v for k, v in singlerun_powers.items() if k in ["boat_1_singlerun", "boat_3_singlerun"]
    }

    # Rename for clarity in the plot (optional but nice)
    renamed_speeds = {
        k.replace("boat_", "singlerun_") for k in relevant_singleruns
    }
    renamed_speeds = {k.replace("boat_", "singlerun_"): v for k, v in relevant_singleruns.items()}
    renamed_powers = {k.replace("boat_", "singlerun_"): v for k, v in relevant_singlerun_powers.items()}

    # Merge
    combined_speeds = {**formation_speeds, **renamed_speeds}
    combined_powers = {**formation_powers, **renamed_powers}

    # Plot all
    plot_formation_comparison(combined_speeds, combined_powers, output_name="formation_vs_singlerun_20maj")

    # Save results
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = Path(OUT_DIR) / "processed_boat_data.json"
    with open(out_path, "w") as f:
        json.dump(all_runs_by_file, f, indent=2)

    print(f"\n Done. Saved processed data to {out_path}")
