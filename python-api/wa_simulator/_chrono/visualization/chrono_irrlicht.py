# WA Simulator
from wa_simulator.visualization.visualization import WAVisualization

# Chrono specific imports
import pychrono as chrono
import pychrono.vehicle as veh
import pychrono.irrlicht as irr

# Other imports
from math import ceil

# ------------------
# WA Chrono Irrlicht
# ------------------


class WAChronoIrrlicht(WAVisualization):
    def __init__(self, vehicle, system):
        self.app = veh.ChVehicleIrrApp(vehicle.GetVehicle())
        self.app.SetHUDLocation(500, 20)
        self.app.SetSkyBox()
        self.app.AddTypicalLogo()
        self.app.AddTypicalLights(
            irr.vector3df(-150.0, -150.0, 200.0),
            irr.vector3df(-150.0, 150.0, 200.0),
            100,
            100,
        )
        self.app.AddTypicalLights(
            irr.vector3df(150.0, -150.0, 200.0),
            irr.vector3df(150.0, 150.0, 200.0),
            100,
            100,
        )
        self.app.SetChaseCamera(chrono.ChVectorD(0.0, 0.0, 1.75), 6.0, 0.5)
        self.app.SetTimestep(system.step_size)

        self.app.AssetBindAll()
        self.app.AssetUpdateAll()

        self.render_steps = int(ceil(system.render_step_size / system.step_size))

        self.system = system

    def Advance(self, step):
        if self.system.GetStepNumber() % self.render_steps == 0:
            self.app.BeginScene(True, True, irr.SColor(255, 140, 161, 192))
            self.app.DrawAll()
            self.app.EndScene()

        self.app.Advance(step)

    def Synchronize(self, time, vehicle_inputs):
        if isinstance(vehicle_inputs, dict):
            d = veh.Inputs()
            d.m_steering = vehicle_inputs["steering"]
            d.m_throttle = vehicle_inputs["throttle"]
            d.m_braking = vehicle_inputs["braking"]
            vehicle_inputs = d
        elif not isinstance(vehicle_inputs, veh.Inputs):
            print("Synchronize: Driver inputs not recognized.")
            exit()

        self.app.Synchronize("", vehicle_inputs)

    def IsOk(self):
        return self.app.GetDevice().run()

    def GetApp(self):
        return self.app
