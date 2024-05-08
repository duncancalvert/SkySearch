# imports
from djitellopy import Tello
import time
import cv2
import math


def tello_connect():
    # Start Connection With Drone
    tello = Tello()
    tello.connect()
    # Get Battery Info
    print(tello.get_battery())
    # Start Camera Display Stream
    tello.streamon()
    frame_read = tello.get_frame_read()


def tello_takeoff():
    Tello.takeoff()


def get_keyboard_input():
    # In reality you want to display frames in a seperate thread. Otherwise
    #  they will freeze while the drone moves.
    while True:
        img = Tello_Connect.frame_read.frame
        cv2.imshow("drone", img)

        key = cv2.waitKey(1) & 0xff
        if key == ord("p"): # ESC
            Tello.land()
            break
        elif key == ord('w'):
            Tello.move_forward(30)
        elif key == ord('s'):
            Tello.move_back(30)
        elif key == ord('a'):
            Tello.move_left(30)
        elif key == ord('d'):
            Tello.move_right(30)
        elif key == ord('e'):
            Tello.rotate_clockwise(30)
        elif key == ord('q'):
            Tello.rotate_counter_clockwise(30)
        elif key == ord('r'):
            Tello.move_up(30)
        elif key == ord('f'):
            Tello.move_down(30)


