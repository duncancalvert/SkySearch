import os
import cv2
import sys

# Make the current working directory the directory above so that we can call our source python files
def add_to_path(path:str) -> None:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), path)))
    
add_to_path("..")
add_to_path("../src")


from src.LLM import LLM
from src.LLM import Info
from src.UAV import UAV
from src.GroundControl import GroundControl


def main():

    # All starting inforation
    # drone_ip = "10.0.0.178"
    drone_ip = "192.168.87.33"

    if drone_ip is None:
        uav = UAV()
    else:
        uav = UAV(drone_ip)

    uav.connect()
    
    battery = uav.get_battery()
    print(battery)

    # LLM Initialization
    info = Info()

    llm = LLM(info.API_KEY, info.ORGANIZATION, info.PROJECT)

    # Ground control initialization
    gc = GroundControl(uav, llm)

    gc.llm_control("black jacket on a hanger")


    
if __name__ == "__main__":
    print("Executing main")
    main()
    print("Executed main")