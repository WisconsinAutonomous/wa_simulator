import wa_simulator as wa

system = wa.WAChronoSystem(1e-3)

terrain = wa.WAChronoTerrain(wa.EGP_ENV_MODEL_FILE, system)

vehicle = wa.WAChronoVehicle(wa.GO_KART_MODEL_FILE, system)