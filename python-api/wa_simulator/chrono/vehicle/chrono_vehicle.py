# WA Simulator
from wa_simulator.vehicle.vehicle import WAVehicle

# Chrono specific imports
import pychrono as chrono
import pychrono.vehicle as veh

# ---------------
# Utility methods
# ---------------

def ReadVehicleModelFile(filename):
    import json

    full_filename = veh.GetDataFile(filename)

    with open(full_filename) as f:
        j = json.load(f)

    if 'Vehicle' not in j:
        print('\'Vehicle\' not present in the passed json file.')
        exit()
    vehicle_filename = veh.GetDataFile(j['Vehicle']['Input File'])

    if 'Powertrain' not in j:
        print('\'Powertrain\' not present in the passed json file.')
        exit()
    powertrain_filename = veh.GetDataFile(j['Powertrain']['Input File'])

    if 'Tire' not in j:
        print('\'Tire\' not present in the passed json file.')
        exit()
    tire_filename = veh.GetDataFile(j['Tire']['Input File'])

    return vehicle_filename, powertrain_filename, tire_filename


def CreateTireFromJSON(tire_filename):
    import json

    with open(tire_filename) as f:
        j = json.load(f)

    if 'Type' not in j:
        print('\'Type\' not present in the passed json file.')
        exit()

    if j['Type'] != 'Tire':
        print('Passed json file is not a tire file.')
        exit()

    if 'Template' not in j:
        print('\'Template\' not present in the passed json file.')
        exit()

    tire_type = j['Template']
    if tire_type == 'TMeasyTire':
        return veh.TMeasyTire(tire_filename)
    elif tire_type == 'RigidTire':
        return veh.RigidTire(tire_filename)
    else:
        print(f'\'{tire_type}\' not a recognized tire type.')
        exit()

# -----------------
# WA Chrono Vehicle
# -----------------

class WAChronoVehicle(WAVehicle):
    # Global filenames for vehicle models
    GO_KART_MODEL_FILE = 'GoKart/GoKart.json'
    IAC_VEH_MODEL_FILE = 'IAC/IAC.json'

    def __init__(self, filename, system, env, initLoc=chrono.ChVectorD(0, 0, 0.5), initRot=chrono.ChQuaternionD(1, 0, 0, 0)):
        super().__init__("vehicles/GoKart/GoKart_KinematicBicycle.json")
        
        # Get the filenames
        vehicle_file, powertrain_file, tire_file = ReadVehicleModelFile(filename)

        # Create the vehicle
        vehicle = veh.WheeledVehicle(system.GetSystem(), vehicle_file)

        # Initialize the vehicle
        vehicle.Initialize(chrono.ChCoordsysD(initLoc, initRot))

        # Set the visualization components for the vehicle
        vehicle.SetChassisVisualizationType(veh.VisualizationType_PRIMITIVES)
        vehicle.SetSuspensionVisualizationType(veh.VisualizationType_PRIMITIVES)
        vehicle.SetSteeringVisualizationType(veh.VisualizationType_PRIMITIVES)
        vehicle.SetWheelVisualizationType(veh.VisualizationType_NONE)

        # Create the powertrain
        # Assumes a SimplePowertrain
        powertrain = veh.SimplePowertrain(powertrain_file)
        vehicle.InitializePowertrain(powertrain)

        # Create and initialize the tires
        for axle in vehicle.GetAxles():
            tireL = CreateTireFromJSON(tire_file)
            vehicle.InitializeTire(tireL, axle.m_wheels[0], veh.VisualizationType_MESH)
            tireR = CreateTireFromJSON(tire_file)
            vehicle.InitializeTire(tireR, axle.m_wheels[1], veh.VisualizationType_MESH)

        self.vehicle = vehicle
        self.terrain = env.GetTerrain().GetTerrain()

    def GetVehicle(self):
        return self.vehicle

    def SetTerrain(self, terrain):
        self.terrain = terrain

    def Advance(self, step):
        self.vehicle.Advance(step)

    def Synchronize(self, time, driver_inputs):
        if not isinstance(self.terrain, veh.ChTerrain):
            print('Synchronize: Terrain has not been set.')
            exit()

        if isinstance(driver_inputs, dict):
            d = veh.Inputs()
            d.m_steering = driver_inputs["steering"]
            d.m_throttle = driver_inputs["throttle"]
            d.m_braking = driver_inputs["braking"]
            driver_inputs = d
        elif not isinstance(driver_inputs, veh.Inputs):
            raise TypeError('Synchronize: Type for driver inputs not recognized.')

        self.vehicle.Synchronize(time, driver_inputs, self.terrain)
    
    def GetSimpleState(self):
        pos = self.vehicle.GetVehiclePos()
        return pos.x, pos.y, self.vehicle.GetVehicleRot().Q_to_Euler123().z, self.vehicle.GetVehicleSpeed()
