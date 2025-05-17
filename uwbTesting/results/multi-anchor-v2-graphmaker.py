from matplotlib.typing import MarkEveryType
import pandas as pd
import matplotlib.pyplot as plt
import os

DATA_FOLDER = "rawdata/multi-v2"
OUTPUT_FOLDER = "graphs/multi-v2"
WARMUP_COUNT = 20  # Number of warm-up timestamps to ignore in statistics

def ensure_output_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

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

def plot_individual(df, filename, actual_distance, global_xmax, global_ymax, output_folder):
    df = df.copy()
    df = df.sort_values("Timestamp (s)")
    df['Timestamp (s)'] -= df['Timestamp (s)'].iloc[0]
    df = df[df['Timestamp (s)'] <= global_xmax]

    # mark warmup and test periods manually
    df['Mode'] = ['WARMUP' if i < WARMUP_COUNT else 'TEST' for i in range(len(df))]

    plt.figure(figsize=(10, 6))
    plt.plot(df['Timestamp (s)'], df['Anchor-0 (m)'], label='Anchor-0', color='blue', alpha=0.5)
    plt.plot(df['Timestamp (s)'], df['Anchor-1 (m)'], label='Anchor-1', color='green', alpha=0.5)
    plt.plot(df['Timestamp (s)'], df['MiddlePoint (m)'], label='MiddlePoint', color='purple', linestyle='--')

    if actual_distance:
        plt.axhline(y=actual_distance, color='red', linestyle='dotted', linewidth=2, label='Expected Distance')

    modes = df['Mode'].values
    timestamps = df['Timestamp (s)'].values
    for i in range(1, len(modes)):
        if modes[i] != modes[i - 1]:
            plt.axvline(x=timestamps[i], color='black', linestyle='dashed', linewidth=1, alpha=0.5)

    plt.xlim(0, global_xmax * 1.1)
    plt.ylim(0, global_ymax * 1.1)
    plt.xlabel("Timestamp (s)")
    plt.ylabel("Distance (m)")
    plt.title(f"Distance Over Time - {filename}")
    plt.grid(True)
    plt.legend()

    # Compute statistics only from TEST data
    df_test = df[df['Mode'] == 'TEST']
    stats = compute_statistics(df_test, actual_distance)
    min_d, avg_d, max_d, std_dev, mean_err, mae, rmse = stats

    stats_text = (f"Min: {min_d:.3f} m | Avg: {avg_d:.3f} m | Max: {max_d:.3f} m\n"
                  f"Std Dev: {std_dev:.3f} m\n"
                  f"Mean Error: {mean_err:.3f} m\n"
                  f"MAE: {mae:.3f} m\n"
                  f"RMSE: {rmse:.3f} m")

    plt.text(0.05, 0.2, stats_text, transform=plt.gca().transAxes,
              fontsize=10, verticalalignment='top',
              bbox=dict(facecolor='white', alpha=0.8, edgecolor='black'))

    plt.tight_layout()

    out_path = os.path.join(output_folder, f"{filename.replace('.csv', '')}.png")
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")

def plot_combined(all_data, global_xmax, global_ymax, output_folder):
    plt.figure(figsize=(12, 6))
    colors = plt.cm.tab10.colors
    markers = ['o', 's', '^', 'v', '<', '>', 'D', 'p']

    for idx, (filename, df, actual_distance) in enumerate(all_data):
        df = df.copy()
        df = df.sort_values("Timestamp (s)")
        df['Timestamp (s)'] -= df['Timestamp (s)'].iloc[0]
        df = df[df['Timestamp (s)'] <= global_xmax]

        # mark warmup and test periods manually
        df['Mode'] = ['WARMUP' if i < WARMUP_COUNT else 'TEST' for i in range(len(df))]

        t = df['Timestamp (s)']
        m = df['MiddlePoint (m)']
        color = colors[idx % len(colors)]
        marker = markers[idx % len(markers)]

        plt.plot(t, m, label=filename.replace('.csv', ''), color=color, marker=marker, linewidth=1, markersize=3, markevery=5)
        if actual_distance:
            plt.plot(t, [actual_distance] * len(t), linestyle='dashed', color=color, alpha=0.5, marker=marker, markersize=3, markevery=5)

        # Method transitions
        modes = df['Mode'].values
        timestamps = df['Timestamp (s)'].values
        for i in range(1, len(modes)):
            if modes[i] != modes[i - 1]:
                plt.axvline(x=timestamps[i], color='black', linestyle='dashed', linewidth=1, alpha=0.3)

    plt.xlim(0, global_xmax * 1.1)
    plt.ylim(0, global_ymax * 1.1)
    plt.xlabel("Timestamp (s)")
    plt.ylabel("Distance (m)")
    plt.title("Combined MiddlePoint Comparison")
    plt.legend(fontsize=8)
    plt.grid(True)
    plt.tight_layout()

    out_path = os.path.join(output_folder, "combined_plot.png")
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")

def process_all():
    ensure_output_folder(OUTPUT_FOLDER)

    global_xmax = float('inf')
    global_ymax = float('-inf')
    all_data = []

    for file in sorted(os.listdir(DATA_FOLDER)):
        if file.endswith(".csv"):
            path = os.path.join(DATA_FOLDER, file)
            df = pd.read_csv(path)
            df.columns = df.columns.str.strip()
            for col in ['MiddlePoint (m)', 'Anchor-0 (m)', 'Anchor-1 (m)', 'Expected (m)']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            df.dropna(subset=["MiddlePoint (m)"], inplace=True)

            df['Timestamp (s)'] -= df['Timestamp (s)'].iloc[0]
            max_time = df['Timestamp (s)'].max()
            if max_time < global_xmax:
                global_xmax = max_time

            y_columns = ['MiddlePoint (m)', 'Anchor-0 (m)', 'Anchor-1 (m)', 'Expected (m)']
            max_y = df[y_columns].max().max()
            if max_y > global_ymax:
                global_ymax = max_y

            actual_distance = df['Expected (m)'].iloc[0] if 'Expected (m)' in df.columns else None
            all_data.append((file, df, actual_distance))

    for filename, df, actual_distance in all_data:
        plot_individual(df, filename, actual_distance, global_xmax, global_ymax, OUTPUT_FOLDER)

    plot_combined(all_data, global_xmax, global_ymax, OUTPUT_FOLDER)

if __name__ == "__main__":
    process_all()
