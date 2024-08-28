from streamlit_app import main as start_streamlit_app
from UAV import UAV
import threading
from collections import deque
from pynput import keyboard
import time

class GroundControl(object):
    """Singleton object representing our ground control station"""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False  # Add an initialized flag
        return cls._instance

    def __init__(self, UAV) -> None:
        if not self._initialized:
            self.UAV = UAV
            self.command_queue = deque()
            self.queue_lock = threading.Lock()
            self._initialized = True  # Mark as initialized
                
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
        params = [direction, x, reason]
        command_thread = threading.Thread(target=command, args=params)
        command_thread.start()

    def rotate_uav_clockwise(self, x: int, reason: str):
        command = self.UAV.rotate_clockwise
        params = [x, reason]
        command_thread = threading.Thread(target=command, args=params)
        command_thread.start()

    def rotate_uav_counter_clockwise(self, x: int, reason: str):
        command = self.UAV.rotate_counter_clockwise
        params = [x, reason]
        command_thread = threading.Thread(target=command, args=params)
        command_thread.start()

    def flip_uav(self, direction: str, reason: str):
        command = self.UAV.flip
        params = [direction, reason]
        command_thread = threading.Thread(target=command, args=params)
        command_thread.start()

    def takeoff_uav(self, reason: str = None):
        command = self.UAV.takeoff
        params = [reason]
        command_thread = threading.Thread(target=command, args=params)
        command_thread.start()

    def land_uav(self, reason: str):
        command = self.UAV.land
        params = [reason]
        command_thread = threading.Thread(target=command, args=params)
        command_thread.start()
        
    # Check queue
    def idle(self):
        
        def on_press(key):
            try:
                with self.queue_lock:
                    if key.char == 'w':
                        self.command_queue.append("f 40")
                    elif key.char == 'a':
                        self.command_queue.append("l 40")
                    elif key.char == 's':
                        self.command_queue.append("b 40")
                    elif key.char == 'd':
                        self.command_queue.append("r 40")
            except AttributeError:
                pass
        
        listener = keyboard.Listener(on_press=on_press)
        listener.start()
        
        while True:
            # Check if there is anything in the queue, if there is perform the action
            if len(self.command_queue) > 0:
                
                print(self.command_queue)
                
                command = self.command_queue.popleft()
                direction, x = command.split(" ")
                x = int(x)
                self.move_uav(direction=direction, x = x, reason = "Key pressed")
            else:
                time.sleep(.01)

        
if __name__ == "__main__":
    pass