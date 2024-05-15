import cv2
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoHTMLAttributes
import numpy as np
import av
from PIL import Image
import os
import shutil
import torch
import yaml
import mediapipe as mp
import speech_recognition as sr
import threading
import time

# Custom Libraries
from utils import streamlit_html_helper
# from utils import yolo_helper
import testcode
import manual_pilot_mode


# --- How to interact with this application in the terminal:
# Start: streamlit run .../streamlit_app.py
# End: ctrl + d


def main():
    # Initialize the ground control app
    facial_rec_slider, select_coco_classes, radio_button_current_active_skill = streamlit_html_helper.ground_control()
    time.sleep(2)

    if radio_button_current_active_skill == "Nothing":
        pass
    elif radio_button_current_active_skill == "Voice Commands":
        pass
    elif radio_button_current_active_skill == "Hand Signals":
        # Initialize the tello object
        tello, TELLO_IP = manual_pilot_mode.tello_connect()
        time.sleep(2)
        while True:
            testcode.process_video(tello, TELLO_IP)
    else:
        pass


# Run the Streamlit app
if __name__ == "__main__":
    main()
