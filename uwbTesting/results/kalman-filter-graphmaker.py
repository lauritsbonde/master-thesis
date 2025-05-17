import pandas as pd
import matplotlib.pyplot as plt
import os
import re
import numpy as np
from matplotlib.lines import Line2D
import matplotlib.cm as cm

global_xmax = float('inf')
global_ymax = float('-inf')

def extract_distance_from_filename(filename):
    match = re.search(r'kalman-filter-(\d+)', filename)
    return float(match.group(1)) / 100 if match else None

def plot_individual_file(filepath, output_folder, global_xmax, global_ymax):
    df = parse_custom_log_file(filepath)

    xmax_padded = global_xmax * 1.1  # 10% padding
    ymax_padded = global_ymax * 1.1  # 10% padding

    for col in ['Raw-A-0 (m)','Raw-A-1 (m)','KF-A-0 (m)','KF-A-1 (m)','MiddlePoint (m)']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.sort_values('Timestamp (s)')
    # Trim data to stay within global_xmax
    # df['Timestamp (s)'] -= df['Timestamp (s)'].iloc[0]  # Normalize timestamp
    df = df[df['Timestamp (s)'] <= global_xmax]

    actual_distance = extract_distance_from_filename(os.path.basename(filepath))
    if actual_distance is None:
        print(f"Could not extract distance from {filepath}")
        return None

    avg_middle = df[df['Mode'].str.upper() == "TEST"]['MiddlePoint (m)'].mean()

    plt.figure(figsize=(8, 5))

    # Plot each full signal as one line
    plt.plot(df['Timestamp (s)'], df['Raw-A-0 (m)'], linestyle='-', color='blue', label='Raw-anchor-0', alpha=0.25)
    plt.plot(df['Timestamp (s)'], df['Raw-A-1 (m)'], linestyle='-', color='green', label='Raw-anchor-1', alpha=0.25)
    plt.plot(df['Timestamp (s)'], df['KF-A-0 (m)'], linestyle='-', color='orange', label='KF-anchor-0', alpha=0.75)
    plt.plot(df['Timestamp (s)'], df['KF-A-1 (m)'], linestyle='-', color='red', label='KF-anchor-1', alpha=0.75)
    plt.plot(df['Timestamp (s)'], df['MiddlePoint (m)'], linestyle='--', color='purple', label='MiddlePoint')

    # Add actual distance reference
    if actual_distance:
        plt.axhline(y=actual_distance, color='red', linestyle='dotted', linewidth=2, label='Actual Distance')

    # Mark mode transitions with vertical lines
    timestamps = df['Timestamp (s)'].values
    modes = df['Mode'].str.upper().values
    for i in range(1, len(modes)):
        if modes[i] != modes[i - 1]:
            plt.axvline(x=timestamps[i], color='black', linestyle='dashed', linewidth=1, alpha=0.2)

    plt.xlabel('Timestamp (s)')
    plt.ylabel('Distance (m)')
    plt.title(f'Distance Over Time - {os.path.basename(filepath)}')
    plt.grid(True)
    plt.legend(loc='upper right', fontsize=9, frameon=True)

    # Compute and show statistics
    df_valid = df[df['Mode'].str.upper() == "TEST"]
    stats = compute_statistics(df_valid, actual_distance)
    min_d, avg_d, max_d, std_dev, mean_err, mae, rmse = stats

    stats_text = (f"Min: {min_d:.3f} m | Avg: {avg_d:.3f} m | Max: {max_d:.3f} m\n"
                  f"Std Dev: {std_dev:.3f} m\n"
                  f"Mean Error: {mean_err:.3f} m\n"
                  f"MAE: {mae:.3f} m\n"
                  f"RMSE: {rmse:.3f} m")

    # plt.xlim(0, xmax_padded)
    # plt.ylim(0, ymax_padded)

    # plt.text(0.05, 0.24, stats_text, transform=plt.gca().transAxes, fontsize=10,
    #          verticalalignment='top', bbox=dict(facecolor='white', alpha=0.8, edgecolor='black'))

    output_path = os.path.join(output_folder, os.path.basename(filepath).replace('.csv', '.png'))
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"Saved individual plot: {output_path}")

    return actual_distance, avg_middle


def compute_statistics(data, actual_distance):
    avg_distance = data['MiddlePoint (m)'].mean()
    max_distance = data['MiddlePoint (m)'].max()
    min_distance = data['MiddlePoint (m)'].min()
    std_dev = data['MiddlePoint (m)'].std()

    if actual_distance:
        mean_error = (data['MiddlePoint (m)'] - actual_distance).mean()
        mean_abs_error = (data['MiddlePoint (m)'] - actual_distance).abs().mean()
        rmse = ((data['MiddlePoint (m)'] - actual_distance) ** 2).mean() ** 0.5
    else:
        mean_error = mean_abs_error = rmse = None

    return min_distance, avg_distance, max_distance, std_dev, mean_error, mean_abs_error, rmse

def plot_combined_graph_all_lines(file_data, output_folder, global_xmax, global_ymax):
    plt.figure(figsize=(12, 6))

    xmax_padded = global_xmax * 1.1  # 10% padding
    ymax_padded = global_ymax * 1.1  # 10% padding

    markers = ['o', 's', 'D', '^', 'v', '<', '>', 'p', 'h', '*']  # Up to 10
    colors = plt.cm.tab10.colors  # Up to 10 distinct colors

    for idx, (filename, df, actual_distance) in enumerate(file_data):
        marker = markers[idx % len(markers)]
        color = colors[idx % len(colors)]
        label_base = os.path.basename(filename).replace(".csv", "")

        df = df.sort_values('Timestamp (s)')
        # df['Timestamp (s)'] -= df['Timestamp (s)'].iloc[0]
        df = df[df['Timestamp (s)'] <= global_xmax]

        time = df['Timestamp (s)']
        middle = df['MiddlePoint (m)']
        modes = df['Mode'].str.upper().values
        timestamps = time.values

        # Plot middle point
        plt.plot(time, middle, label=f'{label_base} MiddlePoint',
                 color=color, marker=marker, markersize=2, linewidth=1, markevery=15)

        # Plot actual distance
        plt.plot(time, [actual_distance] * len(time), color=color, alpha=0.5, marker=marker, markersize=3, markevery=15)

        # Plot mode change vertical lines
        for i in range(1, len(modes)):
            if modes[i] != modes[i - 1]:
                plt.axvline(x=timestamps[i], color='black', linestyle='dashed', linewidth=1, alpha=0.1)

    plt.xlabel('Timestamp (s)')
    plt.ylabel('Distance (m)')
    plt.title('MiddlePoint vs Actual Distance (All Files)')
    plt.legend(fontsize=8, loc='upper right', ncol=2, frameon=True)
    plt.grid(True)

    plt.xlim(0, xmax_padded)
    plt.ylim(0, ymax_padded)

    output_path = os.path.join(output_folder, 'combined_all_lines_markers.png')
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"Saved combined plot with markers: {output_path}")

def parse_custom_log_file(filepath):
    rows = []
    with open(filepath) as f:
        for line in f:
            match = re.search(
                r"Time: ([\d.]+)s \| Raw0: ([\d.]+) m \| Raw1: ([\d.]+) m \| Filtered0: ([\d.]+) m \| Filtered1: ([\d.]+) m \| Middle: ([\d.]+|nan) m \| Expected: ([\d.]+) m \| Method: (\w+) \| Mode: (\w+)",
                line.strip()
            )
            if match:
                rows.append({
                    "Timestamp (s)": float(match.group(1)),
                    "Raw-A-0 (m)": float(match.group(2)),
                    "Raw-A-1 (m)": float(match.group(3)),
                    "KF-A-0 (m)": float(match.group(4)),
                    "KF-A-1 (m)": float(match.group(5)),
                    "MiddlePoint (m)": float(match.group(6)) if match.group(6) != "nan" else None,
                    "Expected (m)": float(match.group(7)),
                    "Method": match.group(8),
                    "Mode": match.group(9),
                })
    return pd.DataFrame(rows)

def process_csvs(folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    data_points = []
    file_data_for_combined = []
    individual_dfs = []
    global_xmax = float('inf')
    global_ymax = float('-inf')

    for file in sorted(os.listdir(folder)):
        # if file.endswith('.csv') and 'kalman-filter' in file:
        if file.endswith('.csv') and 'subsection' in file:
            filepath = os.path.join(folder, file)
            df = parse_custom_log_file(filepath)

            for col in ['Raw-A-0 (m)','Raw-A-1 (m)','KF-A-0 (m)','KF-A-1 (m)','MiddlePoint (m)']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            # df['Timestamp (s)'] -= df['Timestamp (s)'].iloc[0]

            max_time = df['Timestamp (s)'].max()
            if max_time < global_xmax:
                global_xmax = max_time

            y_columns = ['Raw-A-0 (m)','Raw-A-1 (m)','KF-A-0 (m)','KF-A-1 (m)','MiddlePoint (m)']
            max_y = df[y_columns].max().max()
            if max_y > global_ymax:
                global_ymax = max_y

            actual_distance = extract_distance_from_filename(file)
            if actual_distance is None:
                print(f"Could not extract distance from {file}")
                continue

            avg_middle = df[df['Mode'].str.upper() == "TEST"]['MiddlePoint (m)'].mean()

            data_points.append((actual_distance, avg_middle))
            file_data_for_combined.append((file, df, actual_distance))
            individual_dfs.append((filepath, df))  # Save for plotting later

    for filepath, df in individual_dfs:
        plot_individual_file(filepath, output_folder, global_xmax, global_ymax)

    if data_points:
        plot_combined_graph_all_lines(file_data_for_combined, output_folder, global_xmax, global_ymax)

if __name__ == "__main__":
    raw_folder = os.path.join(os.path.dirname(__file__), "rawdata/kalman-filter")
    out_folder = os.path.join(os.path.dirname(__file__), "graphs/kalman-filter")
    process_csvs(raw_folder, out_folder)
