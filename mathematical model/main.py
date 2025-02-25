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


""" 
# Calculate the drag force on the boat
# The drag force is calculated by the formula:
# Fd = Cd * A * v^2 * alpha
# Cd of a box is 1.09
# alpha is a factor that is used to simulate minimization of drag force, it is a value between 0 and 1
# The drag force is calculated for a single boat
"""
def drag(boat: Boat, coeficientOfDrag: float = 1.09) -> float:
    return coeficientOfDrag * boat.areaUnderWater() * boat.speed**2 * boat.alpha  # Use boat.alpha


'''
def assignAlphaToBoats(boats: List[Boat], formation_positions: List[Tuple[float, float]], 
                        wake_factor=0.2, side_exposure_factor=0.15):
    """
    Assigns an alpha (drag reduction) value to each boat based on its actual formation position.

    Args:
        boats (List[Boat]): List of boats.
        formation_positions (List[Tuple[float, float]]): List of (x, y) positions for boats.
        wake_factor (float): Reduction in drag due to wake shielding.
        side_exposure_factor (float): Increased drag for boats with exposed sides.

    returns:
        None (Modifies `boats` in place)
    """
    # Find min and max y-values (depth in fleet)
    min_y = min(y for _, y in formation_positions)
    max_y = max(y for _, y in formation_positions)

    for i, boat in enumerate(boats):
        x, y = formation_positions[i]

        print("Boat position: x:" + str(x) + ", y: " + str(y))
        print("boat: " + str(i))
        # Normalize row position (0 for front row, 1 for backmost)
        normalized_depth = (y - min_y) / (max_y - min_y) if max_y > min_y else 0
        print("normalized dept: " + str(normalized_depth))

        # Determine side exposure: boats near the edges of the formation have higher exposure
        num_neighbors = sum(1 for j, (x2, y2) in enumerate(formation_positions) if abs(y2 - y) < 0.01)
        print("number of neighbors: " + str(num_neighbors))
        horizontal_exposure = 1 if num_neighbors <= 2 else 0.5  # More exposed if fewer neighbors
        
        # Compute alpha (drag reduction factor)
        boat.alpha = max(
            0.4,  # Ensure minimum drag reduction factor
            1 - (wake_factor * normalized_depth) - (side_exposure_factor * horizontal_exposure)
        )
        print("######################")
'''

"""
# assumption based on different forces: 

first boat:  1.0
Boat inside: (with neighbors and boat behind, better wake-sharing:)  0.6 
Boat at the back (i wake-zonen) (mindre turbulens) 0.7: 
Boat to the side: 0.8
"""
def AlphaBoatFormation(boats: List[Boat], formation_positions: List[Tuple[float, float]]):
    y_groups = {}
    
    for x, y in formation_positions:
        if y not in y_groups:
            y_groups[y] = []
        y_groups[y].append(x)

    # Compute max and min x for each y level
    y_max_x = {y: max(xs) for y, xs in y_groups.items()}
    y_min_x = {y: min(xs) for y, xs in y_groups.items()}
    
    max_y = max(y_groups.keys())
    min_y = min(y_groups.keys())

    i = 0; 
    for boat, (x, y) in zip(boats, formation_positions):
        i =+ 1
        #print(f"Ship {i}: (x={x:.2f}, y={y:.2f})")
        
        max_x, min_x = y_max_x[y], y_min_x[y]

        if y == max_y:  # Back boats
            boat.alpha = 0.8
            print("Front boat)")

        elif x != max_x and x != min_x and y != max_y and y != min_y:  # Middle boats
            boat.alpha = 0.6
            print("middel boat")
        elif x == max_x or x == min_x:  # Side boats
            boat.alpha = 0.7
            print("side boat")
        else:  # Front boat
            boat.alpha = 0
            print("back boat")


def set_alpha_values_halves(boats: List[Boat], formation_positions: List[Tuple[float, float]]):
    # Group boats by their y-values
    y_groups = {}
    for x, y in formation_positions:
        if y not in y_groups:
            y_groups[y] = []
        y_groups[y].append(x)

    # Sort y-values in descending order (from front to back)
    sorted_y_values = sorted(y_groups.keys(), reverse=True)
    
    # Initialize base alpha value
    base_alpha = 1.0  # Start with 1.0 at the frontmost row

    y_alpha_map = {}  # Store alpha values per y-level

    # Assign alpha values per y level, dividing by 2 for each new y level
    for y in sorted_y_values:
        y_alpha_map[y] = base_alpha
        if(base_alpha <= 0.5): 
            base_alpha
        else:
            base_alpha *= 0.95
            
        # Assign the calculated alpha values to the boats
    for boat, (_, y) in zip(boats, formation_positions):
        boat.alpha = y_alpha_map[y]


"""
    Calculate the power usage of the fleet
    GUIDE: 
    mechanical power in WATT: total_drag_force (N) * speed (m/s) 
    Electrical Power required WATT: Mechanical power * n (Efficiency of the propulsion system, often 0.6 - 0.9) that the Watt
    Current: Electrical Power required WATT / Battery Watt 
    
 Args:
        boats List[Boat]: Array of boats in the swarm
        batteryWatt: int: the watt the battery operate on 
        Efficency: 0-1 float: The Efficiency of propulsion system.

    Returns:
        Returnt the total current used for all the boats. 
 
 
 """
def calculatePowerUsage(boats: List[Boat], efficency: float = 1.0) -> float:
  
    total_DragForce = sum(drag(boat) for boat in boats)
    mechanicalPower = total_DragForce * boats[0].speed # Watt 
    Electricpower = mechanicalPower / efficency # Watt 
    
    return Electricpower 

"""
    Based on using 11.1 V batery, this calculate the current used. 
Args: 
    Powerusage: power usage in watt, 
    batteryVolt: the voltage to create the watt. 

"""
def CalculateCurrentUsage(powerUsage: float, batteryVolt: float = 11.1) -> float: 
    current = powerUsage / batteryVolt
    return current

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

######## Assign alpha values based on formation #######
#assignAlphaToBoats(boats, formation_positions) 
AlphaBoatFormation(boats, formation_positions)


# Calculate results
powerUsage = calculatePowerUsage(boats)
whPerDistance = calculateWhPerDistance(boats, distance)

print("Total Power: " + str(powerUsage) + " W")
print("Power per boat: " + str(powerUsage / number_of_boats) + " W")
print("Wh per distance: " + str(whPerDistance) + " Wh/m")

formation.print_formation(formation_positions)