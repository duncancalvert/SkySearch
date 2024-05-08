# imports
from djitellopy import Tello
import time
import manual_pilot_mode
import cv2
import threading


# take off
manual_pilot_mode.tello_connect()
# manually pilot
manual_pilot_mode.get_keyboard_input()

