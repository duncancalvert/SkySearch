from streamlit_app import main as start_streamlit_app
from UAV import UAV
import threading
from collections import deque

class GroundControl(object):
    """Singleton object representing our ground control station"""
        
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.UAV = None
        self.command_queue = deque()
                
    def host_streamlit(self):

        command = start_streamlit_app
        threading.Thread(target=command).start()
        
    def connect_to_uav(self, ip) -> UAV:
        for i in range(5):
            uav = UAV(ip)
            uav.connect()
            try:
                uav.get_battery()
                break
            except:
                print(f"Connection attempt #{i} to {ip} failed")

    # Drone movement commands
    def move_uav(self, direction: str, x: int, reason: str = None):
        command = self.UAV.move
        params = direction, x, reason
        command_thread = threading.Thread(target=command, args=params)
        command_thread.start()

    def rotate_uav_clockwise(self, x: int, reason: str):
        command = self.UAV.rotate_clockwise
        params = x, reason
        command_thread = threading.Thread(target=command, args=params)
        command_thread.start()

    def rotate_uav_counter_clockwise(self, x: int, reason: str):
        command = self.UAV.rotate_counter_clockwise
        params = x, reason
        command_thread = threading.Thread(target=command, args=params)
        command_thread.start()

    def flip_uav(self, x: int, reason: str):
        command = self.UAV.flip
        params = x, reason
        command_thread = threading.Thread(target=command, args=params)
        command_thread.start()

    def takeoff_uav(self, reason: str):
        command = self.UAV.takeoff
        params = reason
        command_thread = threading.Thread(target=command, args=params)
        command_thread.start()

    def land_uav(self, reason: str):
        command = self.UAV.land
        params = reason
        command_thread = threading.Thread(target=command, args=params)
        command_thread.start()
        
    # Check queue
    
    # {r, l, f , b, takeoff,lang}
    
    # publish action with keys
    
    # start_flight: Check queue every roughly 1/10 secs
    
        
if __name__ == "__main__":
    pass