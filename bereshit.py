import grapher 
from drone import Drone

drone = Drone(
    shipMass=165,
    fuelMass=585,
    maxFuel=441,
    startFuel=275,
    mainEngineForce=430,
    mainBurn=0.15,
    secondEngineForce=25,
    secondaryEngineCount=8,
    secondaryBurn=0.009,
    angle=90,
    horizontalSpeed=1700,
    verticalSpeed=47,
    altitude=30000,
    maxRotationSpeed=1,
    thrust=0.7
)

grapher.drawFlightPath(drone)