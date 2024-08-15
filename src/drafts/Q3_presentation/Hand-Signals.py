import cv2
import mediapipe as mp
import time
from djitellopy import Tello

# Drone IP address
TELLO_IP = '192.168.86.22'

# Initialize MediaPipe Hands and Tello drone
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
#drone = Tello(TELLO_IP)
drone = Tello()
# Connect to the drone and start video stream
drone.connect()
print(f"Battery: {drone.get_battery()}%")
drone.streamon()

# Function to execute drone commands with error checking, photo saving, and landmark drawing
def execute_drone_command(command, frame, hand_landmarks):
    try:
        # Save the frame with landmarks drawn
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

        # Pause for 5 seconds after executing a command
        time.sleep(5)
    except Exception as e:
        print(f"An error occurred while executing {command}: {e}")


# Define gestures and corresponding actions
def detect_gesture(landmarks):
    thumbs_up = landmarks[mp_hands.HandLandmark.THUMB_TIP].y < landmarks[mp_hands.HandLandmark.INDEX_FINGER_MCP].y
    thumbs_down = landmarks[mp_hands.HandLandmark.THUMB_TIP].y > landmarks[mp_hands.HandLandmark.WRIST].y
    peace_sign = (landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP].y < landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
                  landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y < landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
                  landmarks[mp_hands.HandLandmark.RING_FINGER_TIP].y > landmarks[mp_hands.HandLandmark.RING_FINGER_PIP].y and
                  landmarks[mp_hands.HandLandmark.PINKY_TIP].y > landmarks[mp_hands.HandLandmark.PINKY_PIP].y)

    if thumbs_up:
        return "takeoff"
    elif thumbs_down:
        return "land"
    elif peace_sign:
        return "flip_back"
    return "none"

# Initialize video capture
cap = cv2.VideoCapture(f'udp://{TELLO_IP}:11111')

frame_skip = 30
frame_count = 0

# Main loop for gesture recognition and control
with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to get frame")
            break

        frame_count += 1
        if frame_count % frame_skip != 0:
            continue  # Skip processing for this frame

        # Process the frame for hand detection
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        # Check for gestures and execute commands
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                gesture = detect_gesture(hand_landmarks.landmark)
                if gesture != "none":
                    execute_drone_command(gesture, frame, results.multi_hand_landmarks)
                    break  # Execute for the first detected hand and break

                # Draw hand landmarks for display
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # Display the frame
        cv2.imshow('Tello Hand Control', frame)

        if cv2.waitKey(5) & 0xFF == 27:  # ESC key to exit
            break

# Cleanup
cap.release()
cv2.destroyAllWindows()
# Ensure the drone lands if the script is stopped, not passing landmarks as not needed here
execute_drone_command('land', frame, [])
drone.streamoff()
