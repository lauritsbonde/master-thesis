import pandas as pd
import matplotlib.pyplot as plt
import os
import re
from matplotlib.lines import Line2D

# Constants
WARM_UP_COUNT = 20
DATA_FOLDER = "rawdata"
OUTPUT_FOLDER = "graphs/single-anchor"

def extract_distance_from_filename(filename):
    match = re.search(r'uwb-test-(\d+)cm', filename)
    return int(match.group(1)) / 100 if match else None

def compute_statistics(data, actual_distance):
    avg = data['Distance (m)'].mean()
    max_val = data['Distance (m)'].max()
    min_val = data['Distance (m)'].min()
    std_dev = data['Distance (m)'].std()
    if actual_distance:
        mean_err = (data['Distance (m)'] - actual_distance).mean()
        mae = (data['Distance (m)'] - actual_distance).abs().mean()
        rmse = ((data['Distance (m)'] - actual_distance) ** 2).mean() ** 0.5
    else:
        mean_err = mae = rmse = None
    return min_val, avg, max_val, std_dev, mean_err, mae, rmse

def plot_individual(df, filename, actual_distance, global_xmax, global_ymax, output_folder):
    df = df.copy()
    df = df.sort_values("Timestamp (s)")
    df['Timestamp (s)'] -= df['Timestamp (s)'].iloc[0]
    df = df[df['Timestamp (s)'] <= global_xmax]

    df['Mode'] = ['WARMUP' if i < WARM_UP_COUNT else 'TEST' for i in range(len(df))]
    df_test = df[df['Mode'] == 'TEST']
    stats = compute_statistics(df_test, actual_distance)

    plt.figure(figsize=(8, 5))
    plt.plot(df['Timestamp (s)'], df['Distance (m)'], color='blue', linestyle='-', label='Measured Distance')

    if actual_distance:
        plt.axhline(y=actual_distance, color='red', linestyle='dotted', linewidth=2, label='Actual Distance')

    transition_time = df['Timestamp (s)'].iloc[WARM_UP_COUNT] if len(df) > WARM_UP_COUNT else None
    if transition_time:
        plt.axvline(x=transition_time, color='black', linestyle='dashed', linewidth=1, alpha=0.5)

    min_d, avg_d, max_d, std_dev, mean_err, mae, rmse = stats
    stats_text = (f"Min: {min_d:.3f} m | Avg: {avg_d:.3f} m | Max: {max_d:.3f} m\n"
                  f"Std Dev: {std_dev:.3f} m\n"
                  f"Mean Error: {mean_err:.3f} m\n"
                  f"MAE: {mae:.3f} m\n"
                  f"RMSE: {rmse:.3f} m")
    plt.text(0.05, 0.25, stats_text, transform=plt.gca().transAxes,
             fontsize=10, verticalalignment='top', bbox=dict(facecolor='white', alpha=0.8, edgecolor='black'))

    plt.xlim(0, global_xmax * 1.1)
    plt.ylim(0, global_ymax * 1.1)
    plt.xlabel('Timestamp (s)')
    plt.ylabel('Distance (m)')
    plt.title(f'Distance Over Time - {os.path.basename(filename)}')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    output_path = os.path.join(output_folder, os.path.basename(filename).replace('.csv', '_stats.png'))
    plt.savefig(output_path)
    plt.close()
    print(f"Saved plot: {output_path}")

def plot_combined(all_data, global_xmax, global_ymax, output_folder):
    plt.figure(figsize=(12, 6))
    colors = plt.cm.tab10.colors
    markers = ['o', 's', '^', 'v', '<', '>', 'D', 'p']
    for idx, (filename, df, actual_distance) in enumerate(all_data):
        df = df.copy()
        df = df.sort_values("Timestamp (s)")
        df['Timestamp (s)'] -= df['Timestamp (s)'].iloc[0]
        df = df[df['Timestamp (s)'] <= global_xmax]
        df['Mode'] = ['WARMUP' if i < WARM_UP_COUNT else 'TEST' for i in range(len(df))]

        t = df['Timestamp (s)']
        d = df['Distance (m)']
        color = colors[idx % len(colors)]
        marker = markers[idx % len(markers)]

        plt.plot(t, d, label=filename.replace('.csv', ''), color=color, marker=marker, linewidth=1, markersize=3, markevery=5)
        if actual_distance:
            plt.plot(t, [actual_distance] * len(t), linestyle='dashed', color=color, alpha=0.5, marker=marker, markersize=3, markevery=5)

        for i in range(1, len(df)):
            if df['Mode'].iloc[i] != df['Mode'].iloc[i - 1]:
                plt.axvline(x=df['Timestamp (s)'].iloc[i], color='black', linestyle='dashed', alpha=0.3)

    plt.xlim(0, global_xmax * 1.1)
    plt.ylim(0, global_ymax * 1.1)
    plt.xlabel("Timestamp (s)")
    plt.ylabel("Distance (m)")
    plt.title("Combined Distance Comparison")
    plt.legend(fontsize=8)
    plt.grid(True)
    plt.tight_layout()

    output_path = os.path.join(output_folder, "combined_plot.png")
    plt.savefig(output_path)
    plt.close()
    print(f"Saved combined plot: {output_path}")

def process_all_csv(rawdata_folder, output_folder):
    global_xmax = float('inf')
    global_ymax = float('-inf')
    all_data = []

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file in sorted(os.listdir(rawdata_folder)):
        if file.endswith(".csv"):
            path = os.path.join(rawdata_folder, file)
            df = pd.read_csv(path)
            df.columns = df.columns.str.strip()
            df = df[['Timestamp (s)', 'Distance (m)']].dropna()
            df = df.sort_values("Timestamp (s)")
            df['Timestamp (s)'] -= df['Timestamp (s)'].iloc[0]

            max_time = df['Timestamp (s)'].max()
            if max_time < global_xmax:
                global_xmax = max_time

            y_columns = ['Distance (m)']
            max_y = df[y_columns].max().max()
            if max_y > global_ymax:
                global_ymax = max_y

            max_time = df['Timestamp (s)'].max()
            max_dist = df['Distance (m)'].max()

            global_xmax = max(global_xmax, max_time)
            global_ymax = max(global_ymax, max_dist)

            actual_distance = extract_distance_from_filename(file)
            all_data.append((file, df, actual_distance))

    for filename, df, actual_distance in all_data:
        plot_individual(df, filename, actual_distance, global_xmax, global_ymax, output_folder)

    plot_combined(all_data, global_xmax, global_ymax, output_folder)

if __name__ == "__main__":
    process_all_csv(DATA_FOLDER, OUTPUT_FOLDER)
