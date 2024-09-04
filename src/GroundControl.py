from streamlit_app import main as start_streamlit_app
from UAV import UAV
from LLM import LLM, Info
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
        
    def perform_first_command(self, reason: str):
        
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

                    self.perform_first_command(reason = "Key pressed")
                
                else:
                    pass
            else:
                time.sleep(.01)
                
    def llm_control(self, description):
                
        prompt = f"""
            Tell me where this object is within the image. Here is a brief description of it: {description}.
            You will have 3 options for the left-right axis and 3 for the vertical axis. In addition, you can tell me if it appears near medium or far. 
            Options: left, center, right. top, center, bottom. near, medium, far.
            In addition, it can also be marked as not present
            Lastly, do not have any inital preference for any of these options, consider them equally as likely to occur
            Only respond with these 3 words or not present, no punctuation or capitalization.
        """
        

        while True:
            
            time.sleep(.1)
            
            if len(self.command_queue) > 0: # If there is an action to be performed then attempt it

                if not self.UAV.is_moving:

                    self.perform_first_command(reason = "LLM Command")
                
                else:
                    pass
            
            else: # Else query the LLM
                
                image = self.UAV.get_frame_read().frame
                processed_image = self.LLM._process_image(image)
                response = self.LLM.api_request(prompt, processed_image)
                content = response['choices'][0]['message']['content']
                split_content = content.split(" ")
                
                if split_content[0] == 'not':
                    self.command_queue.append("cw 45") # idle behavior TODO: Make this somehow pass a different 
                                                       # type of reason to not show LLM Command since this is idle behavior
                elif 'bottom' in content:
                    self.command_queue.append("down 40")
                elif 'top' in content:
                    self.command_queue.append("up 40")
                elif 'left' in content:
                    self.command_queue.append("ccw 45")
                elif 'right' in content:
                    self.command_queue.append("cw 45")
                elif "near" in content:
                    self.command_queue.append("b 40")
                elif "far" in content:
                    self.command_queue.append("f 40")

                

        
        
        
        
        

        
if __name__ == "__main__":
    pass