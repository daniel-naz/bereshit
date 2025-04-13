from moon import Moon
import utils
import math

class Drone:
    DEBUG_PRINT = False
    VALID_ANGLE_ERROR = 0.01
    VALID_VERTICAL_SPEED = 25

    def __init__(self, shipMass: float, fuelMass: float, maxFuel: float, startFuel: float,
                    mainEngineForce: float, mainBurn: float, secondEngineForce: float,
                    secondaryEngineCount: float, secondaryBurn: float, angle: float,
                    horizontalSpeed: float, verticalSpeed: float, altitude: float,
                    maxRotationSpeed: float, thrust : float):   
            
        # ship properties
        self.__shipMass = shipMass
        self.__fuelMass = fuelMass
        self.__maxFuel = maxFuel
        self.__currentFuel = maxFuel if startFuel is None else startFuel
        
        # engine properties
        self.__mainEngineForce = mainEngineForce
        self.__secondEngineForce = secondEngineForce
        self.__secondaryEngineCount = secondaryEngineCount
        self.__mainBurn = mainBurn
        self.__secondaryBurn = secondaryBurn
        
        # physics
        self.__horizontalSpeed = horizontalSpeed
        self.__verticalSpeed = verticalSpeed
        self.__altitude = altitude
        self.__maxRotationSpeed = maxRotationSpeed

        # angle
        self.__angle = angle if angle is not None else math.atan2(horizontalSpeed, verticalSpeed)

        # additional properties
        self.__thrustForce = thrust  # range: [0, 1]
        self.__acceleration = 0
        self.__distance = 0

        self.__startData = (horizontalSpeed, verticalSpeed, altitude, self.__currentFuel, self.__angle, self.__thrustForce, self.__angle)


    def __accelerate(self, useMainEngine : bool, useSecondaryEngine : bool):
        t = 0
        if useMainEngine: t += self.__mainEngineForce
        if useSecondaryEngine: t += self.__secondaryEngineCount * self.__secondEngineForce
        ans = t / self.__getTotalMass()
        return ans
    
    def __getTotalSpeed(self) -> float:
        return math.sqrt(self.__horizontalSpeed ** 2 + self.__verticalSpeed ** 2)

    def __getTotalMass(self) -> float:
        return self.__shipMass + self.__fuelMass * (self.__currentFuel / self.__maxFuel)

    def __useMainEngine(self, dt : float):
        if(self.__currentFuel > 0):
            self.__currentFuel -= dt * self.__mainBurn * self.__thrustForce
            self.__acceleration = self.__accelerate(True, False) * self.__thrustForce

    def __useSecondaryEngines(self, dt : float):
        if(self.__currentFuel > 0):
            self.__currentFuel -= dt * self.__secondaryBurn * self.__secondaryEngineCount * self.__thrustForce
            self.__acceleration = self.__accelerate(False, True) * self.__thrustForce

    def __useAllEngines(self, dt : float):
        if(self.__currentFuel > 0):
            self.__currentFuel -= dt * self.__secondaryBurn * self.__secondaryEngineCount * self.__thrustForce
            self.__currentFuel -= dt * self.__mainBurn * self.__thrustForce
            self.__acceleration = self.__accelerate(True, True) * self.__thrustForce
    
    def __applyPhysics(self, dt: float):
        self.__useAllEngines(dt)

        # Decompose thrust based on ship angle
        ang_rad = math.radians(self.__angle)
        h_acc = math.sin(ang_rad) * self.__acceleration  # Thrust component sideways
        v_acc = math.cos(ang_rad) * self.__acceleration  # Thrust component upward

        # Apply vertical gravity: increases vertical speed (downward)
        v_acc = Moon.get_acc(self.__horizontalSpeed) - v_acc  # Gravity pulls down, thrust pushes up

        # Update horizontal speed
        self.__horizontalSpeed -= h_acc * dt

        # Update vertical speed: positive = falling
        self.__verticalSpeed += v_acc * dt

        # Update position
        self.__distance += self.__horizontalSpeed * dt
        self.__altitude -= self.__verticalSpeed * dt  # Falling decreases altitude

        return (
            self.__horizontalSpeed,
            self.__verticalSpeed,
            self.__distance,
            self.__altitude,
            self.__angle,
            self.__currentFuel,
        )
     
    def reset(self):
        self.__thrustForce = 0  # range: [0, 1]
        self.__acceleration = 0
        self.__distance = 0
        self.__expectedSpeedDecrease = 0  # for calculations
        self.__horizontalSpeed, self.__verticalSpeed, self.__altitude, self.__currentFuel, self.__angle, self.__thrustForce, self.__angle = self.__startData
        
    def getEditableProperties(self):
        return [
            # sider_name, property_name, min, start, max
            ("Start Fuel", "currentFuel", 1, self.__currentFuel, self.__maxFuel),
            ("Horivontal Speed", "horizontalSpeed", 1, self.__horizontalSpeed, 3000),
            ("Vertical Speed", "verticalSpeed", 1, self.__verticalSpeed, 100),
            ("Start Thrust", "thrustForce", 0, self.__thrustForce, 1),
            ("Start Rotation Angle", "angle", 0, self.__angle, 90),
            ("Start Altitude", "altitude", 10000, self.__altitude, 40000),
        ]

    def setData(self, key, value):
        private_key = f"_{self.__class__.__name__}__{key}"  # Handle name-mangling for private attributes
        if value is not None and hasattr(self, private_key):  # Check if attribute exists
            setattr(self, private_key, value)

    def getData(self, name: str):
        val = getattr(self, f"_{self.__class__.__name__}__{name}", None)
        print(f"Getting {name}, value: {val}")
        return getattr(self, f"_{self.__class__.__name__}__{name}", None)

    def getFullFlightPath(self, dt : float, maxtime : float):
        time = [0]
        altitude = [self.__altitude]
        hs = [self.__horizontalSpeed]
        vs = [self.__verticalSpeed]
        rotation = [self.__angle]
        fuel = [self.__currentFuel]
        thrust = [self.__thrustForce]
        mass = [self.__getTotalMass()]
        totaltime = 0

        while totaltime < maxtime and self.__altitude > 0:
            self.update(dt)
            totaltime += dt

            time.append(totaltime)
            altitude.append(self.__altitude)
            hs.append(self.__horizontalSpeed)
            vs.append(self.__verticalSpeed)
            rotation.append(self.__angle)
            fuel.append(self.__currentFuel)
            thrust.append(self.__thrustForce)
            mass.append(self.__getTotalMass())

        return time, altitude, hs, vs, rotation, fuel, thrust, mass

    def update(self, dt):
        # if self.__horizontalSpeed < 1.5:
        #     self.__angle = 0

        wanted_vs = 22
        wanted_vs = 22 if self.__altitude > 10000 else 18 if self.__altitude > 300 else 10 if self.__altitude > 150 else 1.5 
        if wanted_vs < 10:
            wanted_vs = 1

        # set trust based on speed loss & calc how much speed will be added/ removed
        delta_vs = wanted_vs - self.__verticalSpeed
        delta_hs = -self.__horizontalSpeed if abs(self.__horizontalSpeed) > 1.5 else 0

        if delta_vs > 0: delta_vs = 0

        # check angle for min error
        min_error_angle = -1
        min_error = 100000000

        # find max angle 
        max_angle = utils.map_clamp(self.__horizontalSpeed, 0, 1700, 0, 1500, 0, 90)

        if abs(self.__horizontalSpeed) < 1.5: min_error_angle = 0
        elif self.__getTotalSpeed() > 1700: min_error_angle = 90
        else:
            for angle in range(0, int(max_angle), 1):
                accel = self.__accelerate(True, True)
                ang_rad = math.radians(angle)
                h_acc = math.sin(ang_rad) * accel
                v_acc = math.cos(ang_rad) * accel
                v_acc = Moon.get_acc(self.__horizontalSpeed) - v_acc

                hs = self.__horizontalSpeed - h_acc * dt
                vs = self.__verticalSpeed + v_acc * dt

                error =  (abs(hs - 0) + abs(wanted_vs - vs)) ** 2

                if hs < 0: error = 1000000

                if error < min_error:
                    min_error = error
                    min_error_angle = angle

        wanted_angle = min_error_angle
        delta_angle = wanted_angle - self.__angle
        if abs(delta_angle) > 0.1:
            self.__angle += utils.clamp(delta_angle, -1, 1) * dt 

        maxaccl = self.__accelerate(True, True)
        ang_rad = math.radians(self.__angle)
        h_acc = math.sin(ang_rad) * maxaccl
        v_acc = math.cos(ang_rad) * maxaccl

        v_acc = Moon.get_acc(self.__horizontalSpeed) - v_acc

        hs = -h_acc * dt
        vs = v_acc * dt

        # print(delta_vs, vs)

        self.__thrustForce = max(abs(delta_vs / vs) if vs != 0 else 0, delta_hs / hs if abs(hs) > 1.5 else 0)
        # print(str(delta_vs) +  " : " + str(abs(delta_vs / vs) if vs != 0 else 0))
        self.__thrustForce = utils.clamp(self.__thrustForce, 0, 1)

        if self.__getTotalSpeed() > 1700: self.__thrustForce = 1

        data = self.__applyPhysics(dt)

        # Clamp altitude and check for landing
        if self.__altitude <= 5:
            self.__altitude = 0
            if self.__horizontalSpeed > 2.5 or self.__verticalSpeed > 2.5:
                print("💥 Ship exploded on landing! Vertical speed too high:", self.__getTotalSpeed())
            else:   
                print("✅ Landed safely at", self.__getTotalSpeed(), "m/s!")

        self.__acceleration = 0

        if Drone.DEBUG_PRINT: print(data)