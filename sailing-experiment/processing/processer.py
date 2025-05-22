from constants import NOMINAL_VOLTAGE, SAILING_DISTANCE

def find_speed(duration_s):
    """
    Calculate the speed of the boat based on the sailing distance and duration.

    :param duration_s: Duration in seconds
    :return: Speed in meters per second
    """
    if duration_s <= 0:
        raise ValueError("Duration must be greater than zero.")

    speed = SAILING_DISTANCE / duration_s
    return speed

def integrate_power_kwh(measurements, duration_s):
    if not measurements or len(measurements) < 2:
        raise ValueError("At least two measurements are required.")

    total_energy_ws = 0.0  # watt-seconds

    for i in range(1, len(measurements)):
        prev = measurements[i - 1]
        curr = measurements[i]

        dt = (curr["elapsed_ms"] - prev["elapsed_ms"]) / 1000  # seconds
        avg_power = (prev["watt"] + curr["watt"]) / 2

        total_energy_ws += avg_power * dt

    return total_energy_ws / 3600000  # convert to kWh

def process_run(data):
  return {
    "speed": find_speed(data["duration_s"]),
    "power_consumption_kwh": integrate_power_kwh(data["measurements"], data["duration_s"])
  }
