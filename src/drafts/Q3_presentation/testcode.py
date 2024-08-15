import cv2
import mediapipe as mp
import time
from djitellopy import Tello
import speech_recognition as sr
import threading
import streamlit_app


# Function to execute drone commands
def execute_drone_command(command, drone, frame=None, hand_landmarks=None):
    try:
        if frame is not None and hand_landmarks is not None:
            for landmarks in hand_landmarks:
                mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)
            filename = f"{command}_{int(time.time())}.jpg"
            cv2.imwrite(filename, frame)
            print(f"Executed {command} and saved photo with landmarks as {filename}")

        if command == 'takeoff':
            drone.takeoff()
        elif command == 'land':
            drone.land()
        elif command == 'flip_back':
            drone.flip_back()

        time.sleep(5)
    except Exception as e:
        print(f"An error occurred while executing {command}: {e}")


# Define gestures and corresponding actions
def detect_gesture(landmarks):
    thumbs_up = landmarks[mp_hands.HandLandmark.THUMB_TIP].y < landmarks[mp_hands.HandLandmark.INDEX_FINGER_MCP].y
    thumbs_down = landmarks[mp_hands.HandLandmark.THUMB_TIP].y > landmarks[mp_hands.HandLandmark.WRIST].y
    middle_finger_up = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y < landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y

    if thumbs_up:
        return "takeoff"
    elif thumbs_down:
        return "land"
    elif middle_finger_up:
        return "flip_back"
    return "none"


# Initialize video capture with buffering options
cap = cv2.VideoCapture(f'udp://{drone_IP}:11111?fifo_size=1000000&overrun_nonfatal=1')
frame_skip = 60  # Increase frame skip to process fewer frames
frame_count = 0


# Function to process video frames for gesture recognition
def process_video(drone, drone_IP):

    global frame_count
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
                        execute_drone_command(gesture, drone=drone, frame=frame, hand_landmarks=results.multi_hand_landmarks)
                        break  # Execute for the first detected hand and break

            # Display the frame
            cv2.imshow('Tello Hand Control', frame)

            if cv2.waitKey(5) & 0xFF == 27:  # ESC key to exit
                break

    # Cleanup
    cap.release()
    # cv2.destroyAllWindows()
    # execute_drone_command('land')
    # drone.streamoff()


# Thread for video processing
# video_thread = threading.Thread(target=process_video)
# video_thread.start()



# Ensure the drone lands if the script is stopped
# execute_drone_command('land')
# drone.streamoff()
