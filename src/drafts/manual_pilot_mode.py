# imports
from djitellopy import Tello
import time
import cv2
import math


def tello_connect():
    TELLO_IP = "10.0.0.120"
    # Start Connection With Drone
    tello = Tello(TELLO_IP)
    tello.connect()
    print(tello.get_battery())
    tello.streamon()
    return tello, TELLO_IP


def get_keyboard_input():
    # In reality you want to display frames in a seperate thread. Otherwise
    #  they will freeze while the drone moves.
    while True:
        img = tello_connect().frame_read.frame
        cv2.imshow("drone", img)

        key = cv2.waitKey(1) & 0xff
        if key == ord("p"): # ESC
            tello_connect().land()
            break
        elif key == ord('w'):
            tello_connect().move_forward(30)
        elif key == ord('s'):
            tello_connect().move_back(30)
        elif key == ord('a'):
            tello_connect().move_left(30)
        elif key == ord('d'):
            tello_connect().move_right(30)
        elif key == ord('e'):
            tello_connect().rotate_clockwise(30)
        elif key == ord('q'):
            tello_connect().rotate_counter_clockwise(30)
        elif key == ord('r'):
            tello_connect().move_up(30)
        elif key == ord('f'):
            tello_connect().move_down(30)


