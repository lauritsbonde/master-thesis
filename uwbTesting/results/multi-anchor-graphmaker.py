import pandas as pd
import matplotlib.pyplot as plt
import os
import re
import numpy as np
from matplotlib.lines import Line2D

# Constants
ANCHOR_SEPARATION = 0.184  # 18.4 cm in meters
MIDDLE_OFFSET = ANCHOR_SEPARATION / 2  # 9.2 cm in meters
WARM_UP_COUNT = 20  # Number of warm-up timestamps to ignore in statistics
DATA_COUNT = 300  # Number of data points to process

def extract_distance_from_filename(filename):
    """Extracts the actual distance (in meters) from the filename."""
    match = re.search(r'multi-uwb-test-(\d+)cm', filename)
    return int(match.group(1)) / 100 if match else None  # Convert cm to meters

def calculate_middle_distance(anchor_0, anchor_1):
    """Computes the middle distance based on known geometry."""
    return np.sqrt(((anchor_0 ** 2 + anchor_1 ** 2) / 2) - (MIDDLE_OFFSET ** 2))

def plot_csv_graph(filepath, output_folder):
    """Plots two versions of the distance graph from CSV and saves them."""
    df = pd.read_csv(filepath, skipinitialspace=True)
    df.columns = df.columns.str.strip()

    required_columns = ['Timestamp (s)', 'Anchor-0 (m)', 'Anchor-1 (m)']
    if not all(col in df.columns for col in required_columns):
        print(f"Error: CSV file {filepath} must contain {required_columns} columns.")
        return

    actual_distance = extract_distance_from_filename(os.path.basename(filepath))
    df['CalculatedMiddle (m)'] = calculate_middle_distance(df['Anchor-0 (m)'], df['Anchor-1 (m)'])

    df = df.iloc[:DATA_COUNT]  # Limit to first 200 data points
    df_warmup = df.iloc[:WARM_UP_COUNT]
    df_valid = df.iloc[WARM_UP_COUNT - 1:]

    def compute_statistics(data):
        avg_distance = data['CalculatedMiddle (m)'].mean()
        max_distance = data['CalculatedMiddle (m)'].max()
        min_distance = data['CalculatedMiddle (m)'].min()
        std_dev = data['CalculatedMiddle (m)'].std()

        if actual_distance:
            mean_error = (data['CalculatedMiddle (m)'] - actual_distance).mean()
            mean_abs_error = (data['CalculatedMiddle (m)'] - actual_distance).abs().mean()
            rmse = ((data['CalculatedMiddle (m)'] - actual_distance) ** 2).mean() ** 0.5
        else:
            mean_error = mean_abs_error = rmse = None

        return avg_distance, max_distance, min_distance, std_dev, mean_error, mean_abs_error, rmse

    def plot_graph(df_warmup, df_valid, filename_suffix, include_warmup, stats_data):
        """Helper function to generate and save the graph."""
        plt.figure(figsize=(8, 5))


        plt.plot(df_warmup['Timestamp (s)'], df_warmup['Anchor-0 (m)'], linestyle='-', color='gray', alpha=0.5)
        plt.plot(df_warmup['Timestamp (s)'], df_warmup['Anchor-1 (m)'], linestyle='-', color='gray', alpha=0.5)
        plt.plot(df_warmup['Timestamp (s)'], df_warmup['CalculatedMiddle (m)'], linestyle='--', color='gray', alpha=0.5)

        plt.plot(df_valid['Timestamp (s)'], df_valid['Anchor-0 (m)'], linestyle='-', color='blue', label='Anchor-0')
        plt.plot(df_valid['Timestamp (s)'], df_valid['Anchor-1 (m)'], linestyle='-', color='green', label='Anchor-1')
        plt.plot(df_valid['Timestamp (s)'], df_valid['CalculatedMiddle (m)'], linestyle='--', color='purple', label='Calculated Middle')

        if actual_distance:
            plt.axhline(y=actual_distance, color='r', linestyle='dotted', linewidth=2, label='Actual Distance')

        plt.xlabel('Timestamp (s)')
        plt.ylabel('Distance (m)')
        plt.title(f'Distance over time ({os.path.basename(filepath)}) - {filename_suffix}')
        plt.grid(True)

        legend_entries = [
            Line2D([0], [0], color='blue', linestyle='-', linewidth=2, label="Anchor-0"),
            Line2D([0], [0], color='green', linestyle='-', linewidth=2, label="Anchor-1"),
            Line2D([0], [0], color='purple', linestyle='--', linewidth=2, label="Calculated Middle"),
            Line2D([0], [0], color='r', linestyle='dotted', linewidth=2, label="Actual Distance"),
        ] if include_warmup else [
            Line2D([0], [0], color='gray', linestyle='-', linewidth=2, label="Warm-up"),
            Line2D([0], [0], color='blue', linestyle='-', linewidth=2, label="Anchor-0"),
            Line2D([0], [0], color='green', linestyle='-', linewidth=2, label="Anchor-1"),
            Line2D([0], [0], color='purple', linestyle='--', linewidth=2, label="Calculated Middle"),
            Line2D([0], [0], color='r', linestyle='dotted', linewidth=2, label="Actual Distance"),
        ]

        avg_distance, max_distance, min_distance, std_dev, mean_error, mean_abs_error, rmse = stats_data

        stats_text = (f"Min: {min_distance:.3f} m | Avg: {avg_distance:.3f} m | Max: {max_distance:.3f} m\n"
                      f"Std Dev: {std_dev:.3f} m\n"
                      f"Mean Error: {mean_error:.3f} m\n"
                      f"MAE: {mean_abs_error:.3f} m\n"
                      f"RMSE: {rmse:.3f} m")

        plt.text(0.1, 0.26, stats_text, transform=plt.gca().transAxes, fontsize=10,
                 verticalalignment='top', bbox=dict(facecolor='white', alpha=0.8, edgecolor='black'))

        plt.legend(handles=legend_entries, loc='lower right', frameon=True, framealpha=1,
                   handlelength=3, handletextpad=1.5, borderaxespad=1.2, fontsize=10)

        filename = os.path.basename(filepath).replace('.csv', f'_{filename_suffix}.png')
        output_path = os.path.join(output_folder, filename)
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()
        print(f"Saved plot: {output_path}")

    plot_graph(df_warmup, df, "Full", include_warmup=True, stats_data=compute_statistics(df))
    plot_graph(df_warmup, df_valid, "Filtered", include_warmup=False, stats_data=compute_statistics(df_valid))

def process_all_csv(rawdata_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file in os.listdir(rawdata_folder):
        if file.endswith(".csv") and file.startswith("multi-uwb-test"):
            csv_path = os.path.join(rawdata_folder, file)
            plot_csv_graph(csv_path, output_folder)

if __name__ == "__main__":
    rawdata_folder = os.path.join(os.path.dirname(__file__), "rawdata/multi")
    output_folder = os.path.join(os.path.dirname(__file__), "graphs/multi")
    process_all_csv(rawdata_folder, output_folder)
