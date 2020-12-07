# ----------------------------------------------------------------------------------------
# The vehicle class should be a lightweight wrapper for the Chrono vehicle module.
# The purpose of this class is to "hide" the intricacies of the ChVehicle, while
# also providing the ability to be a typical ChVehicle.
#
#
#
# ----------------------------------------------------------------------------------------

import pychrono as chrono
import pychrono.vehicle as veh

# -----------------------------------
# Global filenames for vehicle models
# -----------------------------------
GO_KART_MODEL_FILE = 'GoKart/GoKart.json'
IAC_VEH_MODEL_FILE = 'IAC/IAC.json'

def ReadWAVehicleModelFile(filename):
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
# -----------------------------------
# -----------------------------------

def CreateTireFromJSON(tire_filename):
    import json

    with open(tire_filename) as f:
        j = json.load(f)
    
    if 'Type' not in j:
        print('\'Type\' not present in the passed json file.')
        exit()

    if  j['Type'] != 'Tire':
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

def CreateVehicleFromJSON(wa_filename, step_size, system=None, contact_method=None, initLoc=chrono.ChVectorD(0,0,0.5), initRot=chrono.ChQuaternionD(1,0,0,0)):
    vehicle_file, powertrain_file, tire_file = ReadWAVehicleModelFile(wa_filename)

    # Default contact method is SMC
    if system is None and contact_method is None:
        contact_method = chrono.ChContactMethod_SMC
    
    # Create the vehicle
    if system is not None:
        vehicle = veh.WheeledVehicle(system, vehicle_file)
    else:
        vehicle = veh.WheeledVehicle(vehicle_file, contact_method)
    
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

    # Create and initialize the tires
    for axle in vehicle.GetAxles():
        tireL = CreateTireFromJSON(tire_file)
        vehicle.InitializeTire(tireL, axle.m_wheels[0], veh.VisualizationType_MESH)
        tireR = CreateTireFromJSON(tire_file)
        vehicle.InitializeTire(tireR, axle.m_wheels[1], veh.VisualizationType_MESH)
    
    return vehicle