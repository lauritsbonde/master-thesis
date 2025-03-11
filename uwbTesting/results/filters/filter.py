import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class ExtendedKalmanFilter:
    def __init__(self, initial_state, process_variance, measurement_variance):
        """Initialize EKF with initial state and noise parameters."""
        self.x = np.array([[initial_state], [0]])  # State vector [position, velocity]
        self.P = np.eye(2) * 1.0  # Initial covariance matrix
        self.F = np.array([[1, 1], [0, 1]])  # State transition model
        self.Q = np.array([[process_variance, 0], [0, process_variance]])  # Process noise
        self.H = np.array([[1, 0]])  # Measurement matrix
        self.R = np.array([[measurement_variance]])  # Measurement noise

    def predict(self):
        """Predict step of EKF."""
        self.x = self.F @ self.x  # State prediction
        self.P = self.F @ self.P @ self.F.T + self.Q  # Covariance update

    def update(self, measurement):
        """Update step with new measurement."""
        y = measurement - (self.H @ self.x)  # Measurement residual
        S = self.H @ self.P @ self.H.T + self.R  # Residual covariance
        K = self.P @ self.H.T @ np.linalg.inv(S)  # Kalman gain
        self.x = self.x + K @ y  # Update state estimate
        self.P = (np.eye(2) - K @ self.H) @ self.P  # Update covariance

# Load UWB test data files
file_paths = {
    "30cm": "../rawdata/uwb-test-30cm.csv",
    "40cm": "../rawdata/uwb-test-40cm.csv",
    "50cm": "../rawdata/uwb-test-50cm.csv",
}

data = {}
for key, file in file_paths.items():
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()  # Remove leading/trailing spaces in column names
    data[key] = df

# Apply EKF to UWB data
ekf_results = {}
process_variance = 0.001  # Small process noise
measurement_variance = 0.01  # Measurement noise

for key, df in data.items():
    timestamps = df["Timestamp (s)"].values
    distances = df["Distance (m)"].values

    ekf = ExtendedKalmanFilter(initial_state=distances[0],
                               process_variance=process_variance,
                               measurement_variance=measurement_variance)

    filtered_distances = []
    for d in distances:
        ekf.predict()
        ekf.update(d)
        filtered_distances.append(ekf.x[0, 0])

    ekf_results[key] = (timestamps, filtered_distances)

# Plot results
plt.figure(figsize=(10, 5))
for key, (timestamps, filtered_distances) in ekf_results.items():
    plt.plot(timestamps, filtered_distances, label=f"{key} EKF", linestyle="--")

for key, df in data.items():
    plt.plot(df["Timestamp (s)"], df["Distance (m)"], label=f"{key} Raw", alpha=0.5)

plt.xlabel("Timestamp (s)")
plt.ylabel("Distance (m)")
plt.title("EKF Smoothed UWB Distance Measurements")
plt.legend()
plt.grid()
plt.show()
