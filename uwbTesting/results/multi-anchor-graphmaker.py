import pandas as pd
import matplotlib.pyplot as plt
import os
import re
import numpy as np
from matplotlib.lines import Line2D

# Constants
ANCHOR_SEPARATION = 0.184  # 18.4 cm in meters
MIDDLE_OFFSET = ANCHOR_SEPARATION / 2  # 9.2 cm in meters

def extract_distance_from_filename(filename):
    """Extracts the actual distance (in meters) from the filename."""
    match = re.search(r'multi-uwb-test-(\d+)cm', filename)
    return int(match.group(1)) / 100 if match else None  # Convert cm to meters

def calculate_middle_distance(anchor_0, anchor_1):
    """Computes the middle distance based on known geometry."""
    return np.sqrt(((anchor_0 ** 2 + anchor_1 ** 2) / 2) - (MIDDLE_OFFSET ** 2))

def plot_csv_graph(filepath, output_folder):
    """Plots the distance data from CSV and saves the graph."""
    df = pd.read_csv(filepath, skipinitialspace=True)

    # Strip any leading/trailing spaces in column names
    df.columns = df.columns.str.strip()

    # Check if required columns exist
    required_columns = ['Timestamp (s)', 'Anchor-0 (m)', 'Anchor-1 (m)']
    if not all(col in df.columns for col in required_columns):
        print(f"Error: CSV file {filepath} must contain {required_columns} columns.")
        print("Detected columns:", df.columns.tolist())  # Debugging output
        return

    # Extract actual distance from filename
    actual_distance = extract_distance_from_filename(os.path.basename(filepath))

    # Compute the calculated middle distance
    df['CalculatedMiddle (m)'] = calculate_middle_distance(df['Anchor-0 (m)'], df['Anchor-1 (m)'])

    # Compute statistics for CalculatedMiddle
    avg_distance = df['CalculatedMiddle (m)'].mean()
    max_distance = df['CalculatedMiddle (m)'].max()
    min_distance = df['CalculatedMiddle (m)'].min()
    std_dev = df['CalculatedMiddle (m)'].std()

    if actual_distance:
        mean_error = (df['CalculatedMiddle (m)'] - actual_distance).mean()
        mean_abs_error = (df['CalculatedMiddle (m)'] - actual_distance).abs().mean()
        rmse = ((df['CalculatedMiddle (m)'] - actual_distance) ** 2).mean() ** 0.5
    else:
        mean_error = mean_abs_error = rmse = None

    # Plot the data
    plt.figure(figsize=(8, 5))
    plt.plot(df['Timestamp (s)'], df['Anchor-0 (m)'], linestyle='-', color='blue', label='Anchor-0')
    plt.plot(df['Timestamp (s)'], df['Anchor-1 (m)'], linestyle='-', color='green', label='Anchor-1')
    plt.plot(df['Timestamp (s)'], df['CalculatedMiddle (m)'], linestyle='--', color='purple', label='Calculated Middle')

    # Add a horizontal dotted line for actual distance if available
    if actual_distance:
        plt.axhline(y=actual_distance, color='r', linestyle='dotted', linewidth=2, label='Actual Distance')

    # Labels and title
    plt.xlabel('Timestamp (s)')
    plt.ylabel('Distance (m)')
    plt.title(f'Distance over time ({os.path.basename(filepath)})')
    plt.grid(True)

    # Custom legend entries
    legend_entries = [
        Line2D([0], [0], color='blue', linestyle='-', linewidth=2, label="Anchor-0"),
        Line2D([0], [0], color='green', linestyle='-', linewidth=2, label="Anchor-1"),
        Line2D([0], [0], color='purple', linestyle='--', linewidth=2, label="Calculated Middle"),
        Line2D([0], [0], color='r', linestyle='dotted', linewidth=2, label="Actual Distance"),
    ]

    # Add statistics as text
    stats_text = (f"Min: {min_distance:.3f} m | Avg: {avg_distance:.3f} m | Max: {max_distance:.3f} m\n"
                  f"Std Dev: {std_dev:.3f} m\n"
                  f"Mean Error: {mean_error:.3f} m\n"
                  f"MAE: {mean_abs_error:.3f} m\n"
                  f"RMSE: {rmse:.3f} m")

    plt.text(0.1, 0.26, stats_text, transform=plt.gca().transAxes, fontsize=10,
             verticalalignment='top', bbox=dict(facecolor='white', alpha=0.8, edgecolor='black'))

    # Add legend
    plt.legend(handles=legend_entries, loc='lower right', frameon=True, framealpha=1,
               handlelength=3, handletextpad=1.5, borderaxespad=1.2, fontsize=10)

    # Save the plot
    filename = os.path.basename(filepath).replace('.csv', '.png')
    output_path = os.path.join(output_folder, filename)
    plt.savefig(output_path, bbox_inches='tight')  # Ensure everything fits
    plt.close()
    print(f"Saved plot: {output_path}")

def process_all_csv(rawdata_folder, output_folder):
    """Processes all CSV files in the rawdata folder and generates plots."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file in os.listdir(rawdata_folder):
        if file.endswith(".csv") and file.startswith("multi-uwb-test"):
            csv_path = os.path.join(rawdata_folder, file)
            plot_csv_graph(csv_path, output_folder)

if __name__ == "__main__":
    rawdata_folder = os.path.join(os.path.dirname(__file__), "rawdata")
    output_folder = os.path.join(os.path.dirname(__file__), "graphs")
    process_all_csv(rawdata_folder, output_folder)
