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
    pass



    
if __name__ == "__main__":
    print("Executing main")
    main()
    print("Executed main")