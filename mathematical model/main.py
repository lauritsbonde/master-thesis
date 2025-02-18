import formation
from typing import List, Tuple

class Boat:
    def __init__(self, width, length, height, weight, speed=0):
        self.width = width  # meter
        self.length = length  # meter
        self.height = height  # meter
        self.weight = weight  # kg
        self.speed = speed  # m/s
        self.alpha = 1  # drag reduction factor (to be set later)

    ## Calculate how deep the box is in the water
    def boxDeep(self, waterDensity=1000):
        return self.weight / (waterDensity * self.areaOfBottom())

    ## Calculate the area of the bottom of the box
    def areaOfBottom(self):
        return self.length * self.width

    ## Calculate the area of the box under water pressing against the water
    def areaUnderWater(self):
        return self.boxDeep() * self.width


''' 
# Calculate the drag force on the boat
# The drag force is calculated by the formula:
# Fd = Cd * A * v^2 * alpha
# Cd of a box is 1.09
# alpha is a factor that is used to simulate minimization of drag force, it is a value between 0 and 1
# The drag force is calculated for a single boat
'''
def drag(boat: Boat, coeficientOfDrag: float = 1.09) -> float:
    return coeficientOfDrag * boat.areaUnderWater() * boat.speed**2 * boat.alpha  # Use boat.alpha

def assignAlphaToBoats(boats: List[Boat], formation_positions: List[Tuple[float, float]], 
                        wake_factor=0.2, side_exposure_factor=0.15):
    """
    Assigns an alpha (drag reduction) value to each boat based on its actual formation position.

    Args:
        boats (List[Boat]): List of boats.
        formation_positions (List[Tuple[float, float]]): List of (x, y) positions for boats.
        wake_factor (float): Reduction in drag due to wake shielding.
        side_exposure_factor (float): Increased drag for boats with exposed sides.

    Returns:
        None (Modifies `boats` in place)
    """
    # Find min and max y-values (depth in fleet)
    min_y = min(y for _, y in formation_positions)
    max_y = max(y for _, y in formation_positions)

    for i, boat in enumerate(boats):
        x, y = formation_positions[i]

        # Normalize row position (0 for front row, 1 for backmost)
        normalized_depth = (y - min_y) / (max_y - min_y) if max_y > min_y else 0

        # Determine side exposure: boats near the edges of the formation have higher exposure
        num_neighbors = sum(1 for j, (x2, y2) in enumerate(formation_positions) if abs(y2 - y) < 0.01)
        horizontal_exposure = 1 if num_neighbors <= 2 else 0.5  # More exposed if fewer neighbors

        # Compute alpha (drag reduction factor)
        boat.alpha = max(
            0.4,  # Ensure minimum drag reduction factor
            1 - (wake_factor * normalized_depth) - (side_exposure_factor * horizontal_exposure)
        )

## Calculate the power usage of the fleet
def calculatePowerUsage(boats: List[Boat]) -> float:
    total_power = sum(drag(boat) for boat in boats)
    return total_power

## Calculate the energy used per distance
def calculateWhPerDistance(boats: List[Boat], distance: float) -> float:
    powerUsage = calculatePowerUsage(boats)  # Power in watts (W)
    
    # Time to travel the given distance
    timeToTravel = distance / boats[0].speed  # time in seconds
    
    # Energy used (in Wh)
    energyUsed = (powerUsage * timeToTravel) / 3600  # Convert from Joules to Watt-hours
    
    # Wh per distance
    whPerDistance = energyUsed / distance
    return whPerDistance


# ** Setup & Execution **
number_of_boats = 10
boats = [Boat(1, 1, 1, 10, speed=2) for _ in range(number_of_boats)]
distance = 100  # meters

# Generate formation positions
formation_positions = formation.calculate_formation(number_of_boats)

# Assign alpha values based on formation
assignAlphaToBoats(boats, formation_positions)

# Calculate results
powerUsage = calculatePowerUsage(boats)
whPerDistance = calculateWhPerDistance(boats, distance)

print("Total Power: " + str(powerUsage) + " W")
print("Power per boat: " + str(powerUsage / number_of_boats) + " W")
print("Wh per distance: " + str(whPerDistance) + " Wh/m")