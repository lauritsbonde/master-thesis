

class Boat:
    def __init__(self, width, lenght, height, weight, speed = 0, alphaPositionvalue = 1):
        self.width = width # meter
        self.lenght = lenght # meter
        self.height = height # meter
        self.weight = weight # kg
        self.speed = speed # m/s
        self.alphaPositionvalue = alphaPositionvalue

    '''
    # box deep in the water.
    '''
    def boxDeep(self, waterDensity = 1000): 
        return self.weight / self.areaOfBottom() * waterDensity

    '''
    # Area of the bottom. 
    '''
    def areaOfBottom(self): 
        return self.lenght * self.width
    

    '''
    # Area under the water. 
    '''
    def AreaUnderWater(self): 
        return self.boxDeep() * self.width


def power(thrusters, speed): 
    return thrusters * speed

'''
# coeficientOffdrag: according to nasa: 1.09 for a cube shape link: https://ntrs.nasa.gov/api/citations/20110016614/downloads/20110016614.pdf
# alpha: efficency factor according to the boat position on the sailing shape. 
'''
def drag(boat: Boat, coeficientOffdrag: float = 1.09, alpha = 1) -> float:
      return coeficientOffdrag * boat.AreaUnderWater() * boat.speed**2 * alpha


'''

'''
def calculatePowerUsage(number_of_boats: int, boat: Boat):
    
    acc = 0
    for i in range(number_of_boats): 
        acc += drag(boat, alpha=100-i)
    
    return power(acc, boat.speed)
      

boat = Boat(lenght=0.32, width=0.21, height=0.11, weight=0.7, speed=2)
numberOfboat = 10

print("total drag: " + str(power))
print("drag per boat: " + str(power/numberOfboat))
