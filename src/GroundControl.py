from streamlit_app import main as start_streamlit_app
from UAV import UAV
import threading
from collections import deque
from pynput import keyboard
import time
from openai import OpenAI

class GroundControl(object):
    """Singleton object representing our ground control station"""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False  # Add an initialized flag
        return cls._instance

    def __init__(self, UAV, LLM) -> None:
        if not self._initialized:
            self.UAV = UAV
            self.LLM = LLM
            self.command_queue = deque()
            self.queue_lock = threading.Lock()
            self._initialized = True  # Mark as initialized
                
    def host_streamlit(self):

        command = start_streamlit_app
        threading.Thread(target=command).start()

    # Drone movement commands
    def move_uav(self, direction: str, x: int, reason: str = None):
        command = self.UAV.move
        params = [direction, x, reason]
        command_thread = threading.Thread(target=command, args=params)
        start_time = time.time()
        command_thread.start()
        execution_time = time.time() - start_time

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
    def keyboard_control(self):
        
        key_command_map = {
    'w': "f 40",       # Move forward
    'a': "l 40",       # Move left
    's': "b 40",       # Move backward
    'd': "r 40",       # Move right
    'q': "ccw 45",     # Rotate counter-clockwise
    'e': "cw 45",      # Rotate clockwise
    't': "takeoff",    # Takeoff
    'l': "land",       # Land
    'i': "flip f",     # Flip forward
    'j': "flip l",     # Flip left
    'k': "flip b",     # Flip backward
    'm': "flip r",      # Flip right
    'u': "up 40",
    'o': "down 40"
}

        def on_press(key):
            try:
                with self.queue_lock:
                    if key.char in key_command_map:
                        self.command_queue.append(key_command_map[key.char])
            except AttributeError:
                pass

        listener = keyboard.Listener(on_press=on_press)
        listener.start()
        
        while True:
            if len(self.command_queue) > 0:

                if not self.UAV.is_moving:

                    command = self.command_queue.popleft()
                    action = command.split(" ")[0]
                    
                    if action in ['f', 'b', 'l', 'r']:  # Movement commands
                        direction, x = command.split(" ")
                        x = int(x)
                        self.move_uav(direction=direction, x=x, reason="Key pressed")
                    elif action in ['cw', 'ccw']:  # Rotation commands
                        direction, x = command.split(" ")
                        x = int(x)
                        if action == 'cw':
                            self.rotate_uav_clockwise(x, reason="Key pressed")
                        else:
                            self.rotate_uav_counter_clockwise(x, reason="Key pressed")
                    elif action == 'flip':  # Flip commands
                        direction = command.split(" ")[1]
                        self.flip_uav(direction=direction, reason="Key pressed")
                    elif action in ['up', 'down']:  # Vertical movement commands
                        direction, x = command.split(" ")
                        x = int(x)
                        if action == 'up':
                            self.move_uav(direction='u', x=x, reason="Key pressed")
                        else:
                            self.move_uav(direction='d', x=x, reason="Key pressed")
                    elif action == 'takeoff':
                        self.takeoff_uav(reason="Key pressed")
                    elif action == 'land':
                        self.land_uav(reason="Key pressed")
                
                else:
                    pass
            else:
                time.sleep(.01)
                
    def llm_control(self):
        pass
        
        

        
if __name__ == "__main__":
    pass