from returns.maybe import Maybe
import djitellopy
import logging
import datetime
import uuid

# This will instantiate our logger
logging.basicConfig(filename='drone.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('UAVLogger')

# Disable these other loggers because we will be using our own
djitellopy_logger = logging.getLogger('djitellopy')
djitellopy_logger.setLevel(logging.CRITICAL)
libav_logger = logging.getLogger('libav')
libav_logger.setLevel(logging.CRITICAL)

# Movement dictionary, this can also be used for flips
movement_dict = {
    'f': 'forward',
    'b': 'back',
    'l': 'left',
    'r': 'right',
    'u': 'up',
    'd': 'down'
}

# Rotation dictionary
rotation_dictionary = {
    'cw': 'clockwise',
    'ccw': 'counter-clockwise'
}

# Random Misc. information necessary for the Tello parent class to function
TELLO_IP = '192.168.10.1'
RETRY_COUNT = 3
VS_UDP_PORT = 11111

class UAV(djitellopy.Tello):

    def __init__(self, host=TELLO_IP, retry_count=RETRY_COUNT, vs_udp=VS_UDP_PORT, custom_param=None):
        # Call the parent class's __init__ to retain the existing logic
        super().__init__(host, retry_count, vs_udp)

        self.TAKEOFF_TIMEOUT
        self.is_flying = False
        self.x = 0
        self.y = 0
        self.rotation = 0 # in degrees
        self.height = 100 # in cm
        self.is_moving = False

    def move(self, direction: str, x:int, reason:Maybe[str] = None):
        """Overwrite the move method. Now let's modify stuff """

        direction_str = movement_dict[direction]

        message = f"Moving {direction_str} by {x} cm. Reason: {reason}"
        logging.info(message)

        self.is_moving = True
        # If the direction is down we need to account for how low it gets to the ground
        # sometimes if it get's too low and a down comand is issued then the drone will crash

        if direction == "d" and self.y < 50:
            logging.info(f"Excess downward movement detected, returning None")
            return None
        elif direction == 'd':
            self.y -= x
        self.send_control_command("{} {}".format(direction_str, x))
        self.is_moving = False


    def rotate_clockwise(self, x: int, reason:Maybe[str] = None):
        """Rotate x degree clockwise.
        Arguments:
            x: 1-360
        """

        message = f"Rotating clockwise by {x} degrees. Reason: {reason}"
        self.is_moving = True
        self.send_control_command("cw {}".format(x))
        self.is_moving = False
        logging.info(message)

    def rotate_counter_clockwise(self, x: int, reason:Maybe[str] = None):
        """Rotate x degree counter-clockwise.
        Arguments:
            x: 1-360
        """

        message = f"Rotating counter-clockwise by {x} degrees. Reason: {reason}"
        logging.info(message)
        self.is_moving = True
        self.send_control_command("ccw {}".format(x))
        self.is_moving = False

    def flip(self, direction: str, reason:Maybe[str] = None):
        """Do a flip maneuver.
        Users would normally call one of the flip_x functions instead.
        Arguments:
            direction: l (left), r (right), f (forward) or b (back)
        """

        direction_str = movement_dict[direction]
        message = f"Moving {direction_str}. Reason: {reason}"
        logging.info(message)
        self.is_moving = True
        self.send_control_command("flip {}".format(direction))
        self.is_moving = False

    def takeoff(self, reason: str = None):
        """Automatic takeoff.
        """
        # Something it takes a looooot of time to take off and return a succesful takeoff.
        # So we better wait. Otherwise, it would give us an error on the following calls.

        flight_uuid = str(uuid.uuid4())
        self.current_UUID = flight_uuid
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        current_battery = self.get_battery()
        current_temp = self.get_temperature()
        message = f"Flight initiated at {current_time} with ID: {flight_uuid}. \nCurrent Battery: {current_battery}, Current Temp: {current_temp} Reason: {reason}"
        logging.info(message)
        self.is_moving = True
        self.send_control_command("takeoff", timeout=self.TAKEOFF_TIMEOUT)
        self.is_moving = False
        self.is_flying = True
        self.y = 100

    def land(self, reason:Maybe[str] = None):
        """Automatic landing.
        """

        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        message = f"Flight {self.current_UUID} concluded at {current_time}. Reason: {reason}"
        logging.info(message)

        self.is_moving = True
        self.send_control_command("land")
        self.is_moving = False
        self.y = 0

        self.is_flying = False

    # Option to overwrite these functions:
    # connect
    # connect_to_wifi

if __name__ == "__main__":
    pass