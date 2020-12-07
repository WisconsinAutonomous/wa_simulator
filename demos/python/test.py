import wa_simulator as wa

sys = wa.WAChronoSystem(3e-3)

env = wa.WAChronoEnvironment(wa.EGP_ENV_MODEL_FILE, sys)

veh = wa.WAChronoVehicle(wa.GO_KART_MODEL_FILE, sys, env)

vis = wa.WAChronoIrrlicht(veh, sys)

ctr = wa.WAIrrlichtController(vis, sys)

sim = wa.WASimulation(sys, env, veh, vis, ctr)
sim.Run()