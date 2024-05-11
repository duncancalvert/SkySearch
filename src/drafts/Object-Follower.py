import cv2
import torch
from djitellopy import Tello
import logging

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

# Initialize and connect the Tello drone
# tello = Tello('192.168.87.23')  # <- ZF
tello = Tello('192.168.87.24')  # <- DC
tello.connect()


# Start video streaming
tello.streamon()

# Setup YOLOv5 for object detection
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

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

        logging.info(f"Object detected at ({object_x_center}, {object_y_center}) with area {object_area}/ {total_cam_area}: {TARGET_OBJECT}")

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

# Cleanup
tello.streamoff()
cv2.destroyAllWindows()
tello.land()
