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
    match = re.search(r'calibrated-(\d+\.\d+)', filename)
    return float(match.group(1)) if match else None

def plot_individual_file(filepath, output_folder, global_xmax, global_ymax):
    df = pd.read_csv(filepath, skipinitialspace=True)
    df.columns = df.columns.str.strip()

    xmax_padded = global_xmax * 1.1  # 10% padding
    ymax_padded = global_ymax * 1.1  # 10% padding

    for col in ['MiddlePoint (m)', 'Anchor-0 (m)', 'Anchor-1 (m)', 'Expected (m)']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df.dropna(subset=['MiddlePoint (m)'], inplace=True)
    df = df.sort_values('Timestamp (s)')
    # Trim data to stay within global_xmax
    df['Timestamp (s)'] -= df['Timestamp (s)'].iloc[0]  # Normalize timestamp
    df = df[df['Timestamp (s)'] <= global_xmax]

    actual_distance = extract_distance_from_filename(os.path.basename(filepath))
    if actual_distance is None:
        print(f"Could not extract distance from {filepath}")
        return None

    avg_middle = df[df['Mode'].str.upper() == "TEST"]['MiddlePoint (m)'].mean()

    plt.figure(figsize=(8, 5))

    # Plot each full signal as one line
    plt.plot(df['Timestamp (s)'], df['Anchor-0 (m)'], linestyle='-', color='blue', label='Anchor-0', alpha=0.5)
    plt.plot(df['Timestamp (s)'], df['Anchor-1 (m)'], linestyle='-', color='green', label='Anchor-1', alpha=0.5)
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
    plt.legend(loc='lower right', fontsize=9, frameon=True)

    # Compute and show statistics
    df_valid = df[df['Mode'].str.upper() == "TEST"]
    stats = compute_statistics(df_valid, actual_distance)
    min_d, avg_d, max_d, std_dev, mean_err, mae, rmse = stats

    stats_text = (f"Min: {min_d:.3f} m | Avg: {avg_d:.3f} m | Max: {max_d:.3f} m\n"
                  f"Std Dev: {std_dev:.3f} m\n"
                  f"Mean Error: {mean_err:.3f} m\n"
                  f"MAE: {mae:.3f} m\n"
                  f"RMSE: {rmse:.3f} m")

    plt.xlim(0, xmax_padded)
    plt.ylim(0, ymax_padded)

    plt.text(0.49, 0.95, stats_text, transform=plt.gca().transAxes, fontsize=10,
             verticalalignment='top', bbox=dict(facecolor='white', alpha=0.8, edgecolor='black'))

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
        df['Timestamp (s)'] -= df['Timestamp (s)'].iloc[0]
        df = df[df['Timestamp (s)'] <= global_xmax]

        time = df['Timestamp (s)']
        middle = df['MiddlePoint (m)']
        modes = df['Mode'].str.upper().values
        timestamps = time.values

        # Plot middle point
        plt.plot(time, middle, label=f'{label_base} MiddlePoint',
                 color=color, marker=marker, markersize=2, linewidth=1)

        # Plot actual distance
        plt.plot(time, [actual_distance] * len(time), color=color, alpha=0.5, marker=marker, markersize=3, markevery=5)

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

def process_calibrated_csvs(folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    data_points = []
    file_data_for_combined = []
    individual_dfs = []
    global_xmax = float('inf')
    global_ymax = float('-inf')

    for file in sorted(os.listdir(folder)):
        if file.endswith('.csv') and 'calibrated' in file:
            filepath = os.path.join(folder, file)
            df = pd.read_csv(filepath, skipinitialspace=True)
            df.columns = df.columns.str.strip()

            for col in ['MiddlePoint (m)', 'Anchor-0 (m)', 'Anchor-1 (m)', 'Expected (m)']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            df.dropna(subset=['MiddlePoint (m)'], inplace=True)
            df['Timestamp (s)'] -= df['Timestamp (s)'].iloc[0]

            max_time = df['Timestamp (s)'].max()
            if max_time < global_xmax:
                global_xmax = max_time

            y_columns = ['MiddlePoint (m)', 'Anchor-0 (m)', 'Anchor-1 (m)', 'Expected (m)']
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
    raw_folder = os.path.join(os.path.dirname(__file__), "rawdata/multi-calibrated")
    out_folder = os.path.join(os.path.dirname(__file__), "graphs/multi-calibrated")
    process_calibrated_csvs(raw_folder, out_folder)
