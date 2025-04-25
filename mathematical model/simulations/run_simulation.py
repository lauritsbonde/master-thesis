from formations.elongated_hexagon import create_hexagon_formation
from formations.pyramid_to_line import create_pyramid_to_line
from formations.v_shape import create_v_shape

from energy.power import calculatePowerUsage, calculateWhPerDistance
from utils.visualizer import plot_formation

def print_stats(boats, number_of_boats: int, distance: float):
  power = calculatePowerUsage(boats, efficency=0.8)
  wh_per_meter = calculateWhPerDistance(boats, distance)

  print(f"Total Power: {power:.2f} W")
  print(f"Power per boat: {power / number_of_boats:.2f} W")
  print(f"Wh per distance: {wh_per_meter:.4f} Wh/m")

def run_elongated_hexagon_simulation(number_of_boats: int = 20, distance: float = 100):
  print(f"Running elongated hexagon simulation with {number_of_boats} boats and distance {distance}m")
  boats = create_hexagon_formation(number_of_boats)

  print_stats(boats, number_of_boats, distance)
  return boats

def run_pyramid_to_line_simulation(number_of_boats: int = 20, distance: float = 100):
  print(f"Running pyramid to line simulation with {number_of_boats} boats and distance {distance}m")
  boats = create_pyramid_to_line(number_of_boats)

  print_stats(boats, number_of_boats, distance)
  return boats

def run_v_shape_simulation(number_of_boats: int = 20, distance: float = 100):
  print(f"Running V shape simulation with {number_of_boats} boats and distance {distance}m")
  boats = create_v_shape(number_of_boats)

  print_stats(boats, number_of_boats, distance)
  return boats


def plot_boats(boats, formation_name: str, with_plot: bool = True):
  if not with_plot:
    return
  plot_formation(boats, formation_name)

def run_simulation(with_plot: bool = True):
  number_of_boats = 20
  distance = 100  # meters

  boats = [];

  boats = run_elongated_hexagon_simulation(number_of_boats, distance)
  plot_boats(boats, "elongated_hexagon", with_plot)

  boats = run_pyramid_to_line_simulation(number_of_boats, distance)
  plot_boats(boats, "pyramid_to_line", with_plot)

  boats = run_v_shape_simulation(number_of_boats, distance)
  plot_boats(boats, "v_shape", with_plot)
