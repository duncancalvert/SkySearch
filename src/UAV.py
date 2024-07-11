import djitellopy
import logging
import datetime
import uuid

# This will instantiate our logger
logging.basicConfig(filename='drone.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Disable these other loggers because we will be using our own
djitellopy_logger = logging.getLogger('djitellopy')
djitellopy_logger.setLevel(logging.CRITICAL)
libav_logger = logging.getLogger('libav')
libav_logger.setLevel(logging.CRITICAL)

class UAV(djitellopy.Tello):

    def __init__(self):
        super().__init__()

        self.TAKEOFF_TIMEOUT
        self.is_flying = False

    def move(self, direction: str, x:int):
        """Overwrite the move method. Now let's modify stuff """

        self.send_control_command("{} {}".format(direction, x))


    def rotate_clockwise(self, x: int):
        """Rotate x degree clockwise.
        Arguments:
            x: 1-360
        """
        self.send_control_command("cw {}".format(x))

    def rotate_counter_clockwise(self, x: int):
        """Rotate x degree counter-clockwise.
        Arguments:
            x: 1-360
        """
        self.send_control_command("ccw {}".format(x))

    def flip(self, direction: str):
        """Do a flip maneuver.
        Users would normally call one of the flip_x functions instead.
        Arguments:
            direction: l (left), r (right), f (forward) or b (back)
        """
        self.send_control_command("flip {}".format(direction))

    def takeoff(self):
        """Automatic takeoff.
        """
        # Something it takes a looooot of time to take off and return a succesful takeoff.
        # So we better wait. Otherwise, it would give us an error on the following calls.
        self.send_control_command("takeoff", timeout=self.TAKEOFF_TIMEOUT)
        self.is_flying = True

    def land(self):
        """Automatic landing.
        """
        self.send_control_command("land")
        self.is_flying = False


if __name__ == "__main__":
    pass