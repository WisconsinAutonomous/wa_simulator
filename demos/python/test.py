import wa_chrono_sim as wa

print()

step_size = 3e-3


# --------------
# Create a track
# --------------
centerline = wa.WABezierPath()
track = wa.WATrack.CreateFromCenterline(centerline)

controller = wa.Controller()

vehicle = wa.CreateVehicleFromJSON(wa.GO_KART_MODEL_FILE, step_size)

environment = wa.CreateEnvironmentFromJSON(wa.EV_GRAND_PRIX_ENVIRONMENT)