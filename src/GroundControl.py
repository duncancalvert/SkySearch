from streamlit_app import main as start_streamlit_app
from UAV import UAV
from LLM import LLM, Info
import threading
from collections import deque
from pynput import keyboard
import time
import logging


logging.basicConfig(filename='drone.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('UAVLogger')

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
            self._initialized = True
            self.all_threads = []
            
    def stop_all_threads(self):
        for thread in self.all_threads:
            thread.join()
                
    def host_streamlit(self):

        command = start_streamlit_app
        threading.Thread(target=command).start()

    # Drone movement commands
    def move_uav(self, direction: str, x: int, reason: str = None):
        command = self.UAV.move
        params = [direction, x, reason]
        command_thread = threading.Thread(target=command, args=params)
        command_thread.start()
        self.all_threads.append(command_thread)
        
    
    def rotate_uav_clockwise(self, x: int, reason: str):
        command = self.UAV.rotate_clockwise
        params = [x, reason]
        command_thread = threading.Thread(target=command, args=params)
        command_thread.start()
        self.all_threads.append(command_thread)


    def rotate_uav_counter_clockwise(self, x: int, reason: str):
        command = self.UAV.rotate_counter_clockwise
        params = [x, reason]
        command_thread = threading.Thread(target=command, args=params)
        command_thread.start()
        self.all_threads.append(command_thread)


    def flip_uav(self, direction: str, reason: str):
        command = self.UAV.flip
        params = [direction, reason]
        command_thread = threading.Thread(target=command, args=params)
        command_thread.start()
        self.all_threads.append(command_thread)


    def takeoff_uav(self, reason: str = None):
        command = self.UAV.takeoff
        params = [reason]
        command_thread = threading.Thread(target=command, args=params)
        command_thread.start()
        self.all_threads.append(command_thread)


    def land_uav(self, reason: str):
        command = self.UAV.land
        params = [reason]
        command_thread = threading.Thread(target=command, args=params)
        command_thread.start()
        self.all_threads.append(command_thread)

        
    def perform_first_command(self, reason: str):
        
        command = self.command_queue.popleft()
        action = command.split(" ")[0]
        
        if action in ['f', 'b', 'l', 'r']:  # Movement commands
            direction, x = command.split(" ")
            x = int(x)
            self.move_uav(direction=direction, x=x, reason=reason)
        elif action in ['cw', 'ccw']:  # Rotation commands
            direction, x = command.split(" ")
            x = int(x)
            if action == 'cw':
                self.rotate_uav_clockwise(x, reason=reason)
            else:
                self.rotate_uav_counter_clockwise(x, reason=reason)
        elif action == 'flip':  # Flip commands
            direction = command.split(" ")[1]
            self.flip_uav(direction=direction, reason=reason)
        elif action in ['up', 'down']:  # Vertical movement commands
            direction, x = command.split(" ")
            x = int(x)
            if action == 'up':
                self.move_uav(direction='u', x=x, reason=reason)
            else:
                self.move_uav(direction='d', x=x, reason=reason)
        elif action == 'takeoff':
            self.takeoff_uav(reason=reason)
        elif action == 'land':
            self.land_uav(reason=reason)
        
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
                        logger.info(f"Adding command due to key press: {key_command_map[key.char]}")
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
    
    def query_llm(self,prompt):
        logger.info(f"Querying LLM with camera")

        image = self.UAV.get_frame_read().frame
        processed_image = self.LLM._process_image(image)
        response = self.LLM.api_request(prompt, processed_image)
        content = response
        return content
                
    def llm_control(self, description, intense_logging = False):
                
        prompt = f"""
            Tell me where this object is within the image. Here is a brief description of it: {description}.
            You will have 3 options for the left-right axis and 3 for the vertical axis. In addition, you can tell me if it appears near medium or far. 
            Options: left, center, right. top, center, bottom. near, medium, far.
            If an object takes up more than 95% of the image it is considered close.
            If it takes up more than 80% but less than 95% it is considered medium.
            And if it takes up less than 80% of the image it is considered far.
            In addition, it can also be marked as not present
            Lastly, do not have any inital preference for any of these options, consider them equally as likely to occur
            Only respond with these 3 words or not present, no punctuation or capitalization.
        """
        
        self.UAV.streamon()
        self.UAV.takeoff(reason = f"Looking for {description} using LLMs")

        if intense_logging:
            logger.info("Takeoff successful")

        while True:
            
            
            # logger.info(f"Current drone location: {self.UAV.x}, {self.UAV.y}")
            time.sleep(.5)
            
            if len(self.command_queue) > 0: # If there is an action to be performed then attempt it
                logger.info(f"Commmand was in the queue: {self.command_queue}")

                if not self.UAV.is_moving:
                    
                    self.stop_all_threads()

                    logger.info(f"Attempting a movement")

                    self.perform_first_command(reason = "LLM Command")
                
                else:

                    pass
            
            else: # Else query the LLM

                rotation_step, up_down_step, lr_step = 20, 10, 20
                content = self.query_llm(prompt)
                time.sleep(.05)
                
                split_content = content.split(" ")

                logger.info(f"Response received from LLM: {content}")
                
                if split_content[0] == 'not':
                    command = f'cw {rotation_step}'
                    logger.info(f"Not present, appending '{command}'")
                    self.command_queue.append(command) # idle behavior TODO: Make this somehow pass a different 
                                                       # type of reason to not show LLM Command since this is idle behavior
                if 'bottom' in content:
                    self.command_queue.append(f"down {up_down_step}")
                if 'top' in content:
                    self.command_queue.append(f"up {up_down_step}")
                if 'left' in content:
                    self.command_queue.append(f"ccw {rotation_step}")
                if 'right' in content:
                    self.command_queue.append(f"cw {rotation_step}")
                if "near" in content:
                    self.command_queue.append(f"b {lr_step}")
                if "far" in content:
                    self.command_queue.append(f"f {lr_step}")
        
if __name__ == "__main__":
    pass