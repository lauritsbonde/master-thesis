from boats.boat import Boat
from typing import List

"""
# Calculate the drag force on the boat
# The drag force is calculated by the formula:
# Fd = Cd * A * v^2 * alpha
# Cd of a box is 1.09
# alpha is a factor that is used to simulate minimization of drag force, it is a value between 0 and 1
# The drag force is calculated for a single boat
"""
def drag(boat: Boat, coeficientOfDrag: float = 1.09) -> float:
    return coeficientOfDrag * boat.areaUnderWater() * boat.speed**2.0 * boat.alpha  # Use boat.alpha

"""
    Calculate the power usage of the fleet
    GUIDE:
    mechanical power in WATT: total_drag_force (N) * speed (m/s)
    Electrical Power required WATT: Mechanical power * n (Efficiency of the propulsion system)
    Current: Electrical Power required WATT / Battery Watt

    Args:
        boats List[Boat]: Array of boats in the swarm
        Efficency: 0-1 float: The Efficiency of propulsion system. default is 1.0 (100% efficency)

    Returns:
        Return the total current used for all the boats.
 """
def calculatePowerUsage(boats: List[Boat], efficency: float = 1.0) -> float:

    total_DragForce = sum(drag(boat) for boat in boats)
    mechanicalPower = total_DragForce * boats[0].speed # Watt
    electricPower = mechanicalPower / efficency # Watt

    return electricPower

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

def calculateTotalEnergyKWh(boats: List[Boat], distance: float) -> float:
    powerUsage = calculatePowerUsage(boats)  # Power in watts (W)
    timeToTravel = distance / boats[0].speed  # time in seconds

    # Energy in watt-seconds (joules), then convert to kWh
    energyUsedWh = (powerUsage * timeToTravel) / 3600  # Wh
    energyUsedKWh = energyUsedWh / 1000  # Convert to kWh

    return energyUsedKWh
