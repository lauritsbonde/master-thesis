import os
import json

real_world_data = None;

def read_real_world_file():
  global real_world_data
  if real_world_data is not None:
    return real_world_data
  file_path = "../sailing-experiment/out/processed_boat_data.json"
  if not os.path.exists(file_path):
    raise FileNotFoundError(f"File not found: {file_path}")

  with open(file_path, 'r') as file:
    data = json.load(file)
    real_world_data = data
    return data

  return None

def find_double_speed():
    data = read_real_world_file()
    if data is None:
        print("No data to validate against.")
        return 0.0

    speeds = []

    for key, runs in data.items():
        if "double" in key:
            for run in runs:
                if not run.get("invalid", False) and "_2_" not in run and "speed" in run:
                    speeds.append(run["speed"])

    if not speeds:
        print("No valid speed entries found for doubles.")
        return 0.0

    average_speed = sum(speeds) / len(speeds)
    return average_speed

def find_single_boat_speed():
  data = read_real_world_file()
  if data is None:
    print("No data to validate against.")
    return 0.0

  speeds = []

  for key, runs in data.items():
    if "singlerun" in key and "_2_" not in key:
      for run in runs:
        if not run.get("invalid", False) and "speed" in run:
          speeds.append(run["speed"])

  if not speeds:
    print("No valid speed entries found for single boats.")
    return 0.0

  average_speed = sum(speeds) / len(speeds)

  print(f"Average speed for single boats: {average_speed:.3f} m/s")

  return average_speed

def find_double_boat_kwh():
  data = read_real_world_file()
  if data is None:
    print("No data to validate against.")
    return 0.0

  kwh = []

  for key, runs in data.items():
    if "double" in key:
      for run in runs:
        if not run.get("invalid", False) and "kwh" in run:
          kwh.append(run["kwh"])

  if not kwh:
    print("No valid kWh entries found for doubles.")
    return 0.0

  average_kwh = sum(kwh) / len(kwh)
  return average_kwh

def find_single_boat_kwh():
  data = read_real_world_file()
  if data is None:
    print("No data to validate against.")
    return 0.0

  kwh = []

  for key, runs in data.items():
    if "singlerun" in key and "_2_" not in key:
      for run in runs:
        if not run.get("invalid", False) and "kwh" in run:
          kwh.append(run["kwh"])

  if not kwh:
    print("No valid kWh entries found for single boats.")
    return 0.0

  average_kwh = sum(kwh) / len(kwh)
  return average_kwh

def percentage_diff(a: float, b: float) -> float:
    if a == 0:
        return float('inf')  # avoid division by zero
    return abs(a - b) / abs(a) * 100

def percentage_diff_smart(a: float, b: float, min_threshold: float = 0.001) -> float:
    # If both are very small, use absolute difference
    if abs(a) < min_threshold and abs(b) < min_threshold:
        return 0.0  # treat as no significant difference
    if abs(a) < min_threshold or abs(b) < min_threshold:
        return float('inf')  # one is basically zero, huge mismatch
    return abs(a - b) / max(abs(a), abs(b)) * 100

def validate_with_real_experiment(results):
    data = read_real_world_file()
    if data is None:
        print("No data to validate against.")
        return {"valid": [], "suspicious": []}

    valid_runs = []
    suspicious_runs = []

    for result in results:
        simulated_kwh = result["Total Energy (kWh)"]
        simulated_speed = result.get("Speed")
        formation_name = result["Formation"]

        for key, runs in data.items():
            if formation_name not in key:
                continue

            for run in runs:
                if run.get("invalid", False):
                    continue

                entry = {"key": key}
                is_suspicious = False

                # Check kWh
                if "power_consumption_kwh" in run:
                    real_kwh = run["power_consumption_kwh"]
                    diff_kwh = percentage_diff_smart(real_kwh, simulated_kwh)
                    entry.update({
                        "simulated_kwh": simulated_kwh,
                        "real_kwh": real_kwh,
                        "kwh_diff_pct": diff_kwh
                    })
                    if diff_kwh > 10:
                        is_suspicious = True
                        print(f"⚠️  {key} kWh mismatch: {real_kwh:.6f} vs {simulated_kwh:.6f} ({diff_kwh:.2f}%)")

                # Check speed
                if "speed" in run and simulated_speed is not None:
                    real_speed = run["speed"]
                    diff_speed = percentage_diff_smart(real_speed, simulated_speed)
                    entry.update({
                        "simulated_speed": simulated_speed,
                        "real_speed": real_speed,
                        "speed_diff_pct": diff_speed
                    })
                    if diff_speed > 10:
                        is_suspicious = True
                        print(f"⚠️  {key} speed mismatch: {real_speed:.3f} vs {simulated_speed:.3f} ({diff_speed:.2f}%)")

                (suspicious_runs if is_suspicious else valid_runs).append(entry)

    return {"valid": valid_runs, "suspicious": suspicious_runs}
