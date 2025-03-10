import pandas as pd
import matplotlib.pyplot as plt
import os
import re
from matplotlib.lines import Line2D  # Import for custom legend entry

def extract_distance_from_filename(filename):
    match = re.search(r'uwb-test-(\d+)cm', filename)
    return int(match.group(1)) / 100 if match else None  # Convert to meters

def plot_csv_graph(filepath, output_folder):
    # Read the CSV file and ensure proper parsing
    df = pd.read_csv(filepath, skipinitialspace=True)

    # Strip any leading/trailing spaces in column names
    df.columns = df.columns.str.strip()

    # Check if the required columns exist
    if 'Timestamp (s)' not in df.columns or 'Distance (m)' not in df.columns:
        print("Error: CSV file must contain 'Timestamp (s)' and 'Distance (m)' columns.")
        print("Detected columns:", df.columns.tolist())  # Debugging output
        return

    # Extract actual distance from filename
    actual_distance = extract_distance_from_filename(os.path.basename(filepath))

    # Compute statistics
    avg_distance = df['Distance (m)'].mean()
    max_distance = df['Distance (m)'].max()
    min_distance = df['Distance (m)'].min()
    std_dev = df['Distance (m)'].std()

    if actual_distance:
        mean_error = (df['Distance (m)'] - actual_distance).mean()
        mean_abs_error = (df['Distance (m)'] - actual_distance).abs().mean()
        rmse = ((df['Distance (m)'] - actual_distance) ** 2).mean() ** 0.5
    else:
        mean_error = mean_abs_error = rmse = None

    # Plot the data
    plt.figure(figsize=(8, 5))
    plt.plot(df['Timestamp (s)'], df['Distance (m)'], linestyle='-', color='blue', label='Measured Distance')

    # Add a horizontal dotted line for actual distance if available
    if actual_distance:
        plt.axhline(y=actual_distance, color='r', linestyle='dotted', linewidth=2, label='Actual Distance')

    # Labels and title
    plt.xlabel('Timestamp (s)')
    plt.ylabel('Distance (m)')
    plt.title('Distance over time')
    plt.grid(True)

    # Custom legend entries
    legend_entries = [
        Line2D([0], [0], color='blue', linestyle='-', linewidth=2, label="Measured Distance"),
        Line2D([0], [0], color='r', linestyle='dotted', linewidth=2, label="Actual Distance"),
    ]

    # Add statistics as text instead of inside the legend
    stats_text = (f"Min: {min_distance:.3f} m | Avg: {avg_distance:.3f} m | Max: {max_distance:.3f} m\n"
                  f"Std Dev: {std_dev:.3f} m\n"
                  f"Mean Error: {mean_error:.3f} m\n"
                  f"MAE: {mean_abs_error:.3f} m\n"
                  f"RMSE: {rmse:.3f} m")

    plt.text(0.1, 0.26, stats_text, transform=plt.gca().transAxes, fontsize=10,
             verticalalignment='top', bbox=dict(facecolor='white', alpha=0.8, edgecolor='black'))

    # Add legend with proper spacing
    plt.legend(handles=legend_entries, loc='lower right', frameon=True, framealpha=1,
               handlelength=3, handletextpad=1.5, borderaxespad=1.2, fontsize=10)

    # Save the plot
    filename = os.path.basename(filepath).replace('.csv', '.png')
    output_path = os.path.join(output_folder, filename)
    plt.savefig(output_path, bbox_inches='tight')  # Ensure everything fits
    plt.close()
    print(f"Saved plot: {output_path}")

def process_all_csv(rawdata_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file in os.listdir(rawdata_folder):
        if file.endswith(".csv"):
            csv_path = os.path.join(rawdata_folder, file)
            plot_csv_graph(csv_path, output_folder)

if __name__ == "__main__":
    rawdata_folder = os.path.join(os.path.dirname(__file__), "rawdata")
    output_folder = os.path.join(os.path.dirname(__file__), "graphs")
    process_all_csv(rawdata_folder, output_folder)
