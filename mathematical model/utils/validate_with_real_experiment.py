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
                if not run.get("invalid", False) and run.get("_2_", False) and "speed" in run:
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

def validate_with_real_experiment(results):
    data = read_real_world_file()
    if data is None:
        print("No data to validate against.")
        return

    for result in results:
        simulated_kwh = result["Total Energy (kWh)"]
        simulated_speed = result["Power per Boat (W)"]
        formation_name = result["Formation"]

        # Match with keys in real data
        for key, runs in data.items():
            if formation_name in key:  # "double" in "boat_3_double_back", etc.
                for run in runs:
                    if not run.get("invalid", False):
                        if "power_consumption_kwh" in run:
                            diff = percentage_diff(run["power_consumption_kwh"], simulated_kwh)
                            if diff > 10:
                                print(f"⚠️  {key} kWh mismatch: {run['power_consumption_kwh']:.6f} vs {simulated_kwh:.6f} ({diff:.2f}%)")

                        if "speed" in run:
                            diff = percentage_diff(run["speed"], result.get("Speed", run["speed"]))  # use stored result or estimate
                            if diff > 10:
                                print(f"⚠️  {key} speed mismatch: {run['speed']:.3f} vs {simulated_speed:.3f} ({diff:.2f}%)")
