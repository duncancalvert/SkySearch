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

class UAV(djitellopy.Tello):

    def __init__(self):
        super().__init__()

        self.TAKEOFF_TIMEOUT
        self.is_flying = False

    def move(self, direction: str, x:int, reason:Maybe[str] = None):
        """Overwrite the move method. Now let's modify stuff """

        direction_str = movement_dict[direction]

        message = f"Moving {direction_str} by {x} cm. Reason: {reason}"
        logger.info(message)

        self.send_control_command("{} {}".format(direction, x))


    def rotate_clockwise(self, x: int, reason:Maybe[str] = None):
        """Rotate x degree clockwise.
        Arguments:
            x: 1-360
        """

        message = f"Rotating clockwise by {x} degrees. Reason: {reason}"

        self.send_control_command("cw {}".format(x))
        logger.info(message)

    def rotate_counter_clockwise(self, x: int, reason:Maybe[str] = None):
        """Rotate x degree counter-clockwise.
        Arguments:
            x: 1-360
        """

        message = f"Rotating counter-clockwise by {x} degrees. Reason: {reason}"
        logger.info(message)

        self.send_control_command("ccw {}".format(x))

    def flip(self, direction: str, reason:Maybe[str] = None):
        """Do a flip maneuver.
        Users would normally call one of the flip_x functions instead.
        Arguments:
            direction: l (left), r (right), f (forward) or b (back)
        """

        direction_str = movement_dict[direction]
        message = f"Moving {direction_str}. Reason: {reason}"
        logger.info(message)

        self.send_control_command("flip {}".format(direction))

    def takeoff(self, reason:Maybe[str] = None):
        """Automatic takeoff.
        """
        # Something it takes a looooot of time to take off and return a succesful takeoff.
        # So we better wait. Otherwise, it would give us an error on the following calls.

        flight_uuid = str(uuid.uuid4())
        self.current_UUID = flight_uuid
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        message = f"Flight initiated at {current_time} with ID: {flight_uuid}. Reason: {reason}"
        logging.info(message)

        self.send_control_command("takeoff", timeout=self.TAKEOFF_TIMEOUT)
        self.is_flying = True

    def land(self, reason:Maybe[str] = None):
        """Automatic landing.
        """

        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        message = f"Flight {self.current_UUID} concluded at {current_time}. Reason: {reason}"
        logging.info(message)

        self.send_control_command("land")
        self.is_flying = False

    # Option to overwrite these functions:
    # connect
    # connect_to_wifi

if __name__ == "__main__":
    pass