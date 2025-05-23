class Boat:
    def __init__(self,id, width=0.210, length=0.320, height=0.110, weight=5, speed=0.0, alpha=1.0, position=None):
        self.id = id  # unique identifier for the boat (index)
        self.width = width  # meter
        self.length = length  # meter
        self.height = height  # meter
        self.weight = weight  # kg
        self.speed = speed  # m/s
        self.alpha = alpha # some constant factor to reduce drag
        self.position = position if position is not None else (0, 0)  # (x, y) coordinates

    ## Calculate how deep the box is in the water
    def boxDeep(self, waterDensity=1000):
        return self.weight / (waterDensity * self.areaOfBottom())

    ## Calculate the area of the bottom of the box - used to calculate water displacement
    def areaOfBottom(self) -> float:
        return self.length * self.width

    ## Calculate the area of the box under water pressing against the water
    def areaUnderWater(self) -> float:
        hull_area = self.boxDeep() * self.width
        motor_holder_area = 0.01 * self.width
        return hull_area + motor_holder_area

    def compute_power_usage(self, base_drag: float) -> float:
        # Power = Drag * some factor (simplified model)
        return base_drag * self.alpha

# Boat shape
BOAT_SHAPE = [
    (0.0, 1.0),
    (0.5, 0.25),
    (0.5, -0.25),
    (0.0, -1.0),
    (-0.5, -0.25),
    (-0.5, 0.25),
    (0.0, 1.0)
]
