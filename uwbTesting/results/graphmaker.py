import pandas as pd
import matplotlib.pyplot as plt
import os
import re

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
    actual_distance_text = f"Actual Distance: {actual_distance}m" if actual_distance else "Actual Distance: Unknown"

    # Calculate statistics
    avg_distance = df['Distance (m)'].mean()
    max_distance = df['Distance (m)'].max()
    min_distance = df['Distance (m)'].min()
    std_dev = df['Distance (m)'].std()
    total_time = df['Timestamp (s)'].iloc[-1] - df['Timestamp (s)'].iloc[0]

    if actual_distance:
        mean_error = (df['Distance (m)'] - actual_distance).mean()
        mean_abs_error = (df['Distance (m)'] - actual_distance).abs().mean()
        rmse = ((df['Distance (m)'] - actual_distance) ** 2).mean() ** 0.5
    else:
        mean_error = None
        mean_abs_error = None
        rmse = None

    # Format error metrics
    mean_error_text = f"Mean Error (Bias): {mean_error:.3f} m" if mean_error is not None else ""
    mean_abs_error_text = f"MAE: {mean_abs_error:.3f} m" if mean_abs_error is not None else ""
    rmse_text = f"RMSE: {rmse:.3f} m" if rmse is not None else ""
    std_dev_text = f"Std Dev: {std_dev:.3f} m"

    # Plot the data
    plt.figure(figsize=(8, 5))
    plt.plot(df['Timestamp (s)'], df['Distance (m)'], linestyle='-', label='Distance (m)')

    # Labels and title
    plt.xlabel('Timestamp (s)')
    plt.ylabel('Distance (m)')
    plt.title('Distance vs Timestamp')
    plt.grid(True)

    # Add legend with insights
    legend_text = (f'{actual_distance_text}\n'
                   f'Min: {min_distance:.3f} m - Avg: {avg_distance:.3f} m - Max: {max_distance:.3f} m\n'
                   f'{std_dev_text}\n'
                   f'{mean_error_text}\n'
                   f'{mean_abs_error_text}\n'
                   f'{rmse_text}\n')
    plt.legend([legend_text], loc='lower right', frameon=True, fontsize=10)

    # Save the plot
    filename = os.path.basename(filepath).replace('.csv', '.png')
    output_path = os.path.join(output_folder, filename)
    plt.savefig(output_path)
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
