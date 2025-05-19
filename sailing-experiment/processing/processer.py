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

def find_power_consumption_kwh(measurements, duration_s):
    """
    Calculate the energy consumption in kilowatt-hours (kWh)
    using average current and fixed voltage.

    :param measurements: List of dicts with "current_measure" (in amps)
    :param duration_s: Duration in seconds
    :return: Power consumption in kWh
    """
    if duration_s <= 0:
        raise ValueError("Duration must be greater than zero.")
    if not measurements:
        raise ValueError("No measurements provided.")

    total_current = sum(m["current_measure"] for m in measurements)
    average_current = total_current / len(measurements)

    # Energy in joules: P = I * V * t
    energy_joules = average_current * NOMINAL_VOLTAGE * duration_s

    # Convert to kWh - 1 kWh = 3.6 million joules
    energy_kwh = energy_joules / 3_600_000
    return energy_kwh

def process_run(data):
  return {
    "speed": find_speed(data["duration_s"]),
    "power_consumption": find_power_consumption_kwh(data["measurements"], data["duration_s"])
  }
