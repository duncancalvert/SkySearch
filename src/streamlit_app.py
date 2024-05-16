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
from djitellopy import Tello
import logging


# Custom Libraries
import streamlit_html_helper
# from utils import yolo_helper


# --- How to interact with this application in the terminal:
# Start: streamlit run .../streamlit_app.py
# End: ctrl + d


def tello_connect():
    tello_ip = "192.168.87.29"
    # Start Connection With Drone
    tello = Tello(tello_ip)
    tello.connect()
    print(tello.get_battery())
    tello.streamon()
    return tello, tello_ip


LOG_BLACKLIST = [
    "ERROR:libav.h264:non-existing PPS 0 referenced",
    "ERROR:libav.h264:decode_slice_header error",
    "ERROR:libav.h264:no frame!",
    "INFO:djitellopy:Response streamon: 'ok'",
    "INFO:djitellopy:Send command: 'streamon'",
    "INFO:djitellopy:Tello instance was initialized. Host: '192.168.87.24'. Port: '8889'.",
    "INFO:djitellopy:Send command: 'cw 15'",
    "INFO:djitellopy:Response cw 15: 'ok'",
    "INFO:djitellopy:Send command: 'flip f'"
]

# Initialize logging
logging.basicConfig(filename='drone.log', level=logging.INFO)


class BlacklistFilter(logging.Filter):
    def __init__(self, blacklist):
        super().__init__()
        self.blacklist = blacklist

    def filter(self, record):
        return not any(message in record.getMessage() for message in self.blacklist)


# Remove blacklisted log messages
logger = logging.getLogger()
for message in LOG_BLACKLIST:
    # Add a filter to remove all occurrences of the blacklisted message
    logger.addFilter(BlacklistFilter([message]))


def main():
    # Initialize the ground control app
    facial_rec_slider, select_coco_classes, radio_button_current_active_skill = streamlit_html_helper.ground_control()
    time.sleep(2)
    tello, tello_ip = tello_connect()

    if radio_button_current_active_skill == "Nothing":
        pass

    elif radio_button_current_active_skill == "Voice Commands":
        pass

    elif radio_button_current_active_skill == "Hand Signals":

        # Initialize MediaPipe Hands
        mp_drawing = mp.solutions.drawing_utils
        mp_hands = mp.solutions.hands
        frame_skip = 60  # Increase frame skip to process fewer frames
        frames_counts = 0

        # Function to execute drone commands
        def execute_drone_command(command, frame=None, hand_landmarks=None):
            try:
                if frame is not None and hand_landmarks is not None:
                    for landmarks in hand_landmarks:
                        mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)
                    filename = f"{command}_{int(time.time())}.jpg"
                    cv2.imwrite(filename, frame)
                    print(f"Executed {command} and saved photo with landmarks as {filename}")

                if command == 'takeoff':
                    tello.takeoff()
                elif command == 'land':
                    tello.land()
                elif command == 'flip_back':
                    tello.flip_back()

                time.sleep(5)
            except Exception as e:
                print(f"An error occurred while executing {command}: {e}")

        # Define gestures and corresponding actions
        def detect_gesture(landmarks):
            thumbs_up = landmarks[mp_hands.HandLandmark.THUMB_TIP].y < landmarks[
                mp_hands.HandLandmark.INDEX_FINGER_MCP].y
            thumbs_down = landmarks[mp_hands.HandLandmark.THUMB_TIP].y > landmarks[mp_hands.HandLandmark.WRIST].y
            middle_finger_up = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y < landmarks[
                mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y

            if thumbs_up:
                return "takeoff"
            elif thumbs_down:
                return "land"
            elif middle_finger_up:
                return "flip_back"
            return "none"

        cap = cv2.VideoCapture(f'udp://{tello_ip}:11111?fifo_size=1000000&overrun_nonfatal=1')

        def process_video(frame_count):
            # Function to process video frames for gesture recognition
            with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        print("Failed to get frame")
                        break

                    frame_count += 1
                    if frame_count % frame_skip != 0:
                        continue  # Skip processing for this frame

                    # Resize frame for faster processing
                    frame = cv2.resize(frame, (320, 240))

                    # Process the frame for hand detection
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = hands.process(frame_rgb)

                    # Check for gestures and execute commands
                    if results.multi_hand_landmarks:
                        for hand_landmarks in results.multi_hand_landmarks:
                            gesture = detect_gesture(hand_landmarks.landmark)
                            if gesture != "none":
                                execute_drone_command(gesture, frame=frame,
                                                      hand_landmarks=results.multi_hand_landmarks)
                                break  # Execute for the first detected hand and break

                    # Display the frame
                    # cv2.imshow('Tello Hand Control', frame)

                    if cv2.waitKey(5) & 0xFF == 27:  # ESC key to exit
                        break

                # Cleanup
                cap.release()
                cv2.destroyAllWindows()
                # execute_drone_command('land')
                # tello.streamoff()

        while True:
            process_video(frame_count=frames_counts)


    elif radio_button_current_active_skill == "Find Something":
        # Setup YOLOv8 for object detection
        model = torch.hub.load('ultralytics/yolov5', 'yolov5s.pt', pretrained=True)

        # Define the target object type to track
        TARGET_OBJECT = 'bottle'  # Change this to track different objects

        # Constants for drone control based on the object's size and center position
        OBJECT_TARGET_AREA = 1400  # Adjust based on trial to maintain 2 feet distance
        OBJECT_CENTER_TOLERANCE = 50  # Pixel tolerance for centering
        FRAME_CENTER = (480, 360)  # Assuming 960x720 resolution for simplicity

        frame = tello.get_frame_read().frame
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = model(frame_rgb)

        tello.takeoff()

        num_rots = 0

        while True:
            frame = tello.get_frame_read().frame
            if frame is None:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = model(frame_rgb)

            # Filter detections for the target object
            detections = results.pandas().xyxy[0]
            target_detections = detections[detections['name'] == TARGET_OBJECT]

            # Recalculate frame center in case of resolution changes
            FRAME_CENTER = (frame.shape[1] // 2, frame.shape[0] // 2)

            # Calculate total camera area for distance calculation
            total_cam_area = frame.shape[1] * frame.shape[0]

            # Calculate area for each detection and find the largest one
            if target_detections.empty:  # Detect no bottles
                tello.rotate_clockwise(15)

                num_rots += 1

                if num_rots % 18 == 0:
                    tello.move_down(20)
                    num_rots = 0

            else:  # Detect bottles
                target_detections['area'] = (target_detections['xmax'] - target_detections['xmin']) * \
                                            (target_detections['ymax'] - target_detections['ymin'])

                target_detection = target_detections[target_detections['area'] == target_detections['area'].max()]

                # Calculate center of the target object
                object_area = target_detection['area']

                object_x_center = (target_detection['xmin'] + target_detection['xmax']) / 2
                object_y_center = (target_detection['ymin'] + target_detection['ymax']) / 2
                object_center = ((target_detection['xmin'] + target_detection['xmax']) / 2,
                                 (target_detection['ymin'] + target_detection['ymax']) / 2)

                logging.info(
                    f"Object detected at ({object_x_center}, {object_y_center}) with area {object_area}/ {total_cam_area}: {TARGET_OBJECT}")

                if target_detection['area'].values[0] > OBJECT_TARGET_AREA:
                    tello.flip_forward()
                    tello.move_forward(20)
                    # Log the forward movement
                    logging.info(f"Moving forward to maintain distance: {TARGET_OBJECT}")

                # Adjust drone's position to center the object
                if object_x_center.item() < FRAME_CENTER[0] - OBJECT_CENTER_TOLERANCE:
                    tello.rotate_counter_clockwise(20)
                    # Log the rotation
                    logging.info("Rotating counter clockwise to center the object")
                elif object_x_center.item() > FRAME_CENTER[0] + OBJECT_CENTER_TOLERANCE:
                    tello.rotate_clockwise(20)
                    # Log the rotation
                    logging.info("Rotating clockwise to center the object")

                if object_y_center.item() < FRAME_CENTER[1] - OBJECT_CENTER_TOLERANCE:
                    tello.move_up(20)
                    # Log the upward movement
                    logging.info("Moving up to center the object")
                elif object_y_center.item() > FRAME_CENTER[1] + OBJECT_CENTER_TOLERANCE:
                    tello.move_down(20)
                    # Log the downward movement
                    logging.info("Moving down to center the object")

                # Adjust drone's distance to maintain desired following distance
                if object_area.values[0] > OBJECT_TARGET_AREA:
                    tello.move_back(20)
                    # Log the backward movement
                    logging.info("Moving back to maintain desired following distance")

            rendered_frame = results.render()[0]
            rendered_frame_bgr = cv2.cvtColor(rendered_frame, cv2.COLOR_RGB2BGR)
            cv2.imshow('YOLOv5 Tello Detection', rendered_frame_bgr)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    else:
        pass


# Run the Streamlit app
if __name__ == "__main__":
    main()
