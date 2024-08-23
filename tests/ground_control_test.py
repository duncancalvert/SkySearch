import os
import sys

# Make the current working directory the directory above so that we can call our source python files
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


from src.GroundControl import GroundControl
from src.UAV import UAV


def main():
    print("main started")
    # All starting inforation
    drone_ip = None

    if drone_ip is None:
        uav = UAV()
    else:
        uav = UAV(drone_ip)

    uav.connect()
    
    battery = uav.get_battery()
    print(battery)
    
    gc = GroundControl(uav)
    
    gc.takeoff_uav()
    
    gc.idle()    
    
if __name__ == "__main__":
    print("Executing main")
    main()
    print("Executed main")