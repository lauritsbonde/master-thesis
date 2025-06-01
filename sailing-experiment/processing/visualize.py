import matplotlib.pyplot as plt
import os
import re
from constants import OUT_DIR

def extract_number(filename: str) -> int:
    match = re.search(r'(\d+)', filename)
    return int(match.group(1)) if match else float('inf')

def extract_speed_by_config(data: dict, boats: list[int]):
    result = {b: {"singlerun": [], "front": [], "back": []} for b in boats}

    for filename, runs in data.items():
        boat_num = extract_number(filename)
        if boat_num not in boats:
            continue

        if "singlerun" in filename:
            config = "singlerun"
        elif "double_front" in filename:
            config = "front"
        elif "double_back" in filename:
            config = "back"
        else:
            continue

        values = [
            run["speed"]
            for run in runs
            if not run.get("invalid", False) and "speed" in run
        ]

        result[boat_num][config].extend(values)

    return result

def extract_singlerun_grouped(data: dict, key: str):
    grouped = {}
    for filename, runs in data.items():
        if "singlerun" in filename.lower():
            values = [
                run[key]
                for run in runs
                if not run.get("invalid", False) and key in run
            ]
            if values:
                grouped[filename] = values
    return grouped

def plot_grouped_boxplot(grouped_data: dict, ylabel: str, title: str, output_name: str):
    sorted_items = sorted(grouped_data.items(), key=lambda item: extract_number(item[0]))

    labels = [k for k, _ in sorted_items]
    data = [v for _, v in sorted_items]

    plt.figure(figsize=(10, 6))
    plt.boxplot(data, patch_artist=True, labels=labels)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(rotation=0)
    plt.grid(True, axis="y")
    plt.tight_layout()

    save_path = f"{OUT_DIR}/{output_name}.png"
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, bbox_inches="tight", dpi=300)
    plt.close()

def plot_singlerun_power_and_speed(speeds: dict, powers: dict, output_name: str):
    """
    Plots dual y-axis boxplot for all singlerun files
    - Left Y-axis: Power Consumption (kWh)
    - Right Y-axis: Speed (m/s)
    """
    filenames = sorted(set(speeds.keys()) & set(powers.keys()), key=extract_number)

    speed_data = []
    power_data = []
    labels = []

    for fname in filenames:
        s_vals = speeds[fname]
        p_vals = powers[fname]

        if not s_vals or not p_vals:
            print(f"Warning: Skipping {fname} due to missing data")
            continue

        speed_data.append(s_vals)
        power_data.append(p_vals)
        labels.append(fname)

    if not labels:
        print("No valid singlerun data for combined plot.")
        return

    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax2 = ax1.twinx()

    box_width = 0.35
    positions = list(range(len(labels)))
    offset = 0.2

    # Boxplots
    ax1.boxplot(
        power_data,
        positions=[p - offset for p in positions],
        widths=box_width,
        patch_artist=True,
        boxprops=dict(facecolor="lightblue"),
        medianprops=dict(color="blue"),
    )
    ax2.boxplot(
        speed_data,
        positions=[p + offset for p in positions],
        widths=box_width,
        patch_artist=True,
        boxprops=dict(facecolor="lightgreen"),
        medianprops=dict(color="green"),
    )

    # Overlay data points
    for i, (p_vals, s_vals) in enumerate(zip(power_data, speed_data)):
        ax1.scatter(
            [i - offset] * len(p_vals),
            p_vals,
            color="blue",
            edgecolors="black",
            zorder=3,
            alpha=0.6,
        )
        ax2.scatter(
            [i + offset] * len(s_vals),
            s_vals,
            color="green",
            edgecolors="black",
            zorder=3,
            alpha=0.6,
        )

    ax1.set_ylabel("Power Consumption (kWh)", color="blue")
    ax2.set_ylabel("Speed (m/s)", color="green")
    ax1.set_xticks(positions)
    ax1.set_xticklabels(["boat-1-individual", "boat-2-individual", "boat-3-individual"], rotation=45, ha="right")
    ax1.set_title("Power and Speed Distribution for individual Boats")
    ax1.grid(True, axis="y")

    # Set fixed axis limits
    ax1.set_ylim(0, 0.00175)
    ax2.set_ylim(0, 0.7)

    # Use scientific notation for ax1 (left axis)
    ax1.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))

    ax1.set_ylim(bottom=0)
    ax2.set_ylim(bottom=0)
    fig.tight_layout()

    os.makedirs(OUT_DIR, exist_ok=True)
    plt.savefig(f"{OUT_DIR}/{output_name}.png", bbox_inches="tight", dpi=300)
    plt.close()

def extract_power_by_config(data: dict, boats: list[int]):
    result = {b: {"singlerun": [], "front": [], "back": []} for b in boats}

    for filename, runs in data.items():
        boat_num = extract_number(filename)
        if boat_num not in boats:
            continue

        if "singlerun" in filename:
            config = "singlerun"
        elif "double_front" in filename:
            config = "front"
        elif "double_back" in filename:
            config = "back"
        else:
            continue

        values = [
            run["power_consumption_kwh"]
            for run in runs
            if not run.get("invalid", False) and "power_consumption_kwh" in run
        ]

        result[boat_num][config].extend(values)

    return result

def plot_power_and_speed_comparison_by_boat(power_data: dict, speed_data: dict, save_as: str):
    """
    One plot per boat, each with dual y-axis:
    - Left y-axis: Power Consumption (kWh)
    - Right y-axis: Speed (m/s)
    """
    config_order = ["singlerun", "front", "back"]
    config_labels = {"singlerun": "Single", "front": "Front", "back": "Back"}

    os.makedirs(OUT_DIR, exist_ok=True)

    for boat in sorted(power_data.keys()):
        power_sets = []
        speed_sets = []
        labels = []

        for config in config_order:
            power_vals = power_data[boat][config]
            speed_vals = speed_data[boat][config]

            if not power_vals or not speed_vals:
                print(f"Warning: No data for Boat {boat} - {config}")
                continue

            power_sets.append(power_vals)
            speed_sets.append(speed_vals)
            labels.append(config_labels[config])

        if not power_sets:
            print(f"Skipping Boat {boat} — no valid data.")
            continue

        fig, ax1 = plt.subplots(figsize=(7, 5))
        ax2 = ax1.twinx()

        box_width = 0.35
        positions = list(range(len(power_sets)))
        offset = 0.2

        # Boxplots
        ax1.boxplot(
            power_sets,
            positions=[p - offset for p in positions],
            widths=box_width,
            patch_artist=True,
            boxprops=dict(facecolor="lightblue"),
            medianprops=dict(color="blue"),
        )
        ax2.boxplot(
            speed_sets,
            positions=[p + offset for p in positions],
            widths=box_width,
            patch_artist=True,
            boxprops=dict(facecolor="lightgreen"),
            medianprops=dict(color="green"),
        )

        # Overlay data points
        for i, (p_vals, s_vals) in enumerate(zip(power_sets, speed_sets)):
            ax1.scatter(
                [i - offset] * len(p_vals),
                p_vals,
                color="blue",
                edgecolors="black",
                zorder=3,
                alpha=0.6,
            )
            ax2.scatter(
                [i + offset] * len(s_vals),
                s_vals,
                color="green",
                edgecolors="black",
                zorder=3,
                alpha=0.6,
            )

        ax1.set_ylabel("Power Consumption (kWh)", color="blue")
        ax2.set_ylabel("Speed (m/s)", color="green")
        ax1.set_xticks(positions)
        ax1.set_xticklabels(["individual", "In front", "Behind"])
        ax1.set_title(f"Boat {boat} — Power and Speed by Position (double)")
        ax1.grid(True, axis="y")

        # Set fixed axis limits
        ax1.set_ylim(0, 0.00175)
        ax2.set_ylim(0, 0.7)

        # Use scientific notation for ax1 (left axis)
        ax1.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))

        ax1.set_ylim(bottom=0)
        ax2.set_ylim(bottom=0)
        fig.tight_layout()

        out_path = f"{OUT_DIR}/{save_as}_boat{boat}.png"
        plt.savefig(out_path, bbox_inches="tight", dpi=300)
        plt.close()


def extract_formation_data(data: dict, formations: list[str]) -> tuple[dict, dict]:
    speed_result = {}
    power_result = {}

    for key, runs in data.items():
        normalized_key = key.lower()
        if normalized_key in formations:
            speeds = [r["speed"] for r in runs if not r.get("invalid", False) and "speed" in r]
            powers = [r["power_consumption_kwh"] for r in runs if not r.get("invalid", False) and "power_consumption_kwh" in r]

            if speeds:
                speed_result[normalized_key] = speeds
            if powers:
                power_result[normalized_key] = powers

    return speed_result, power_result

def plot_formation_comparison(speeds: dict, powers: dict, output_name: str):
    import matplotlib.pyplot as plt
    import os

    formations = sorted(set(speeds) & set(powers))
    if not formations:
        print("No matching formation data.")
        return

    speed_data = [speeds[f] for f in formations]
    power_data = [powers[f] for f in formations]
    positions = list(range(len(formations)))
    offset = 0.2

    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax2 = ax1.twinx()

    # Boxplots
    bp1 = ax1.boxplot(
        power_data,
        positions=[p - offset for p in positions],
        widths=0.3,
        patch_artist=True,
        boxprops=dict(facecolor="skyblue"),
        medianprops=dict(color="blue"),
    )
    bp2 = ax2.boxplot(
        speed_data,
        positions=[p + offset for p in positions],
        widths=0.3,
        patch_artist=True,
        boxprops=dict(facecolor="lightgreen"),
        medianprops=dict(color="green"),
    )

    # Overlay individual points
    for i, (p_vals, s_vals) in enumerate(zip(power_data, speed_data)):
        ax1.scatter(
            [i - offset] * len(p_vals),
            p_vals,
            color="blue",
            edgecolors="black",
            alpha=0.6,
            zorder=3
        )
        ax2.scatter(
            [i + offset] * len(s_vals),
            s_vals,
            color="green",
            edgecolors="black",
            alpha=0.6,
            zorder=3
        )

    # Labels and formatting
    ax1.set_ylabel("Power Consumption (kWh)", color="blue")
    ax2.set_ylabel("Speed (m/s)", color="green")
    ax1.set_xticks(positions)
    ax1.set_xticklabels(["diagonal_line", "offset_line", "triangle", "boat_1_individual", "boat_3_individual"], rotation=20)
    ax1.set_title("Power and Speed Comparison")
    ax1.grid(True)

    # Set fixed axis limits
    ax1.set_ylim(0, 0.00175)
    ax2.set_ylim(0, 0.7)

    # Use scientific notation for ax1 (left axis)
    ax1.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))

    fig.tight_layout()
    os.makedirs(OUT_DIR, exist_ok=True)
    plt.savefig(f"{OUT_DIR}/{output_name}.png", dpi=300)
    plt.close()
