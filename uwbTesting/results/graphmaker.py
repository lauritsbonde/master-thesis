import pandas as pd
import matplotlib.pyplot as plt
import os
import re
from matplotlib.lines import Line2D  # Import for custom legend entry

# Constants
WARM_UP_COUNT = 20  # Number of warm-up timestamps to ignore in statistics
DATA_COUNT = 300  # Number of data points to process

def extract_distance_from_filename(filename):
    match = re.search(r'uwb-test-(\d+)cm', filename)
    return int(match.group(1)) / 100 if match else None  # Convert to meters

def plot_csv_graph(filepath, output_folder):
    # Read the CSV file and ensure proper parsing
    df = pd.read_csv(filepath, skipinitialspace=True)
    df.columns = df.columns.str.strip()

    # Check if the required columns exist
    if 'Timestamp (s)' not in df.columns or 'Distance (m)' not in df.columns:
        print("Error: CSV file must contain 'Timestamp (s)' and 'Distance (m)' columns.")
        print("Detected columns:", df.columns.tolist())  # Debugging output
        return

    # Extract actual distance from filename
    actual_distance = extract_distance_from_filename(os.path.basename(filepath))

    # Limit data to the first 200 points
    df = df.iloc[:DATA_COUNT]
    df_warmup = df.iloc[:WARM_UP_COUNT]
    df_valid = df.iloc[WARM_UP_COUNT - 1:]  # Include last warm-up point to maintain continuity

    def compute_statistics(data):
        avg_distance = data['Distance (m)'].mean()
        max_distance = data['Distance (m)'].max()
        min_distance = data['Distance (m)'].min()
        std_dev = data['Distance (m)'].std()

        if actual_distance:
            mean_error = (data['Distance (m)'] - actual_distance).mean()
            mean_abs_error = (data['Distance (m)'] - actual_distance).abs().mean()
            rmse = ((data['Distance (m)'] - actual_distance) ** 2).mean() ** 0.5
        else:
            mean_error = mean_abs_error = rmse = None

        return avg_distance, max_distance, min_distance, std_dev, mean_error, mean_abs_error, rmse

    def plot_graph(df_warmup, df_valid, filename_suffix, stats_data, include_warmup):
        """Helper function to generate and save the graph."""
        plt.figure(figsize=(8, 5))

        # Plot warm-up data in gray
        plt.plot(df_warmup['Timestamp (s)'], df_warmup['Distance (m)'], linestyle='-', color='gray', alpha=0.5)

        # Plot valid data normally
        plt.plot(df_valid['Timestamp (s)'], df_valid['Distance (m)'], linestyle='-', color='blue', label='Measured Distance')

        if actual_distance:
            plt.axhline(y=actual_distance, color='r', linestyle='dotted', linewidth=2, label='Actual Distance')

        plt.xlabel('Timestamp (s)')
        plt.ylabel('Distance (m)')
        plt.title(f'Distance over time ({os.path.basename(filepath)}) - {filename_suffix}')
        plt.grid(True)

        legend_entries = [
            Line2D([0], [0], color='blue', linestyle='-', linewidth=2, label="Measured Distance"),
            Line2D([0], [0], color='r', linestyle='dotted', linewidth=2, label="Actual Distance"),
        ]
        if not include_warmup:
          legend_entries.insert(0, Line2D([0], [0], color='gray', linestyle='-', linewidth=2, label="Warm-up"))

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

    plot_graph(df_warmup, df, "Full", compute_statistics(df), include_warmup=True)
    plot_graph(df_warmup, df_valid, "Filtered", compute_statistics(df_valid), include_warmup=False)

def process_all_csv(rawdata_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file in os.listdir(rawdata_folder):
        if file.endswith(".csv") and file.startswith("uwb-test"):
            csv_path = os.path.join(rawdata_folder, file)
            plot_csv_graph(csv_path, output_folder)

if __name__ == "__main__":
    rawdata_folder = os.path.join(os.path.dirname(__file__), "rawdata")
    output_folder = os.path.join(os.path.dirname(__file__), "graphs")
    process_all_csv(rawdata_folder, output_folder)
