import cv2
import torch
from djitellopy import Tello
from djitellopy.tello import TelloException
import logging
import pathlib
import logging
import datetime
import uuid

# All initial setup

flight_uuid = str(uuid.uuid4())

# Initialize logging
logging.basicConfig(filename='drone.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Let's disable the standard djitellopy logger, these were disabled because they were creating to many logs that weren't informative
djitellopy_logger = logging.getLogger('djitellopy')
djitellopy_logger.setLevel(logging.CRITICAL)

# Now the libav logger as well
libav_logger = logging.getLogger('libav')
libav_logger.setLevel(logging.CRITICAL)

show_image = True

# Initialize and connect the Tello drone
# tello = Tello('192.168.87.22')  # <- ZF
# tello = Tello('192.168.87.24')  # <- DC
tello = Tello() # <- Local
tello.connect()

# Start video streaming
tello.streamon()

# Setup YOLOv5 for object detection
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
model.conf = .2

# model = torch.load(pathlib.Path(__file__).resolve().parent.parent.parent / 'yolov5s.pt')

# Define the target object type to track, we can use a list of objects or a single object. 
# This is because some objects are similar, YOLO had a hard time distinguishing a cup from a bottle
# TARGET_OBJECT = ['cup', 'bowl', 'bottle']
TARGET_OBJECT = "person"


# Constants for drone control based on the object's size and center position
OBJECT_TARGET_COVERAGE = .3  # This constant is used to determine what % of the camera the object should take up.
# This is for distance control
# For smaller objects this value should be lower. For bigger objects it should be higher. For a persion it can be about .3. For a cup it can be .01.

frame = tello.get_frame_read().frame

OBJECT_CENTER_TOLERANCE = 50  # Pixel tolerance for centering
# Calculate total camera area for distance calculation
TOTAL_CAMERA_AREA = None
FRAME_CENTER = None

object_last_position = "right"

current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

# Log the start of our flight
logging.info(f"\n########################################\nFlight {flight_uuid} started at {current_time}, looking for {TARGET_OBJECT}\n current battery={tello.get_battery()}, current temperature={tello.get_temperature()}\n########################################")

tello.takeoff()

# Flight loop
while True:
    frame = tello.get_frame_read().frame
    if frame is None:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = model(frame_rgb)
    
    if show_image:
        rendered_frame = results.render()[0]
        rendered_frame_bgr = cv2.cvtColor(rendered_frame, cv2.COLOR_RGB2BGR)
        cv2.imshow('YOLOv5 Tello Detection', rendered_frame_bgr)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Filter detections for the target object
    detections = results.pandas().xyxy[0]
    
    # Get our dataframe which contains the target objects that YOLO detected, if it detected any
    if isinstance(TARGET_OBJECT, str):
        target_detections = detections[detections['name'] == TARGET_OBJECT]
    elif isinstance(TARGET_OBJECT, list):
        target_detections = detections[detections['name'].isin(TARGET_OBJECT)]
    
    # If we have not yet aquired the area, aquire it
    # We need to do this within the loop because the frame size can change
    if TOTAL_CAMERA_AREA is None or FRAME_CENTER is None:
        TOTAL_CAMERA_AREA = frame.shape[1] * frame.shape[0]
        FRAME_CENTER = (frame.shape[1] // 2, frame.shape[0] // 2)


    if target_detections.empty: # No detections found, so do some default idle behavior
        
        # Rotate around depending on where the object was last seen
        if object_last_position == "left":
            tello.rotate_counter_clockwise(10)
        else:
            tello.rotate_clockwise(10)
        
        logging.info(f"Object last detected {object_last_position} turning {object_last_position}")        


    else:  # Object detected, let's follow it
        
        # Calculate the area of the target object
        target_detections['area'] = (target_detections['xmax'] - target_detections['xmin']) * \
                                    (target_detections['ymax'] - target_detections['ymin'])

        # Get the largest detected object
        target_detection = target_detections[target_detections['area'] == target_detections['area'].max()]

        # Calculate center of the target object and the get the area
        object_area = target_detection['area']
        object_x_center = (target_detection['xmin'] + target_detection['xmax']) / 2
        object_y_center = (target_detection['ymin'] + target_detection['ymax']) / 2
        object_center = ((target_detection['xmin'] + target_detection['xmax']) / 2,
                         (target_detection['ymin'] + target_detection['ymax']) / 2)
        
        target_object_coverage = object_area.item() / TOTAL_CAMERA_AREA
        
        # Center the object in the frame within some tolerance
        if object_x_center.item() < FRAME_CENTER[0] - OBJECT_CENTER_TOLERANCE:
            tello.rotate_counter_clockwise(15)
            logging.info("Rotating counter clockwise to center the object")
        elif object_x_center.item() > FRAME_CENTER[0] + OBJECT_CENTER_TOLERANCE:
            tello.rotate_clockwise(15)
            logging.info("Rotating clockwise to center the object")
        
        else:
            logging.info("X direction is in the sweetspot")

        if object_y_center.item() < FRAME_CENTER[1] - OBJECT_CENTER_TOLERANCE:
            tello.move_up(20)
            logging.info("Moving up to center the object")
        elif object_y_center.item() > FRAME_CENTER[1] + OBJECT_CENTER_TOLERANCE:
            
            # This is in a try-catch block because sometimes the drone can't move down because it's too close to the ground
            try: 
                tello.move_down(20)
                logging.info("Moving down to center the object")

            except TelloException:
                logging.info("Downward movement likely blocked")
                
        else:   
            logging.info("Y Direction is in the sweetspot")
        
        # Let's give our drone some memory to tell where the object last was. On it's right side of vision or left side?
        if object_x_center.item() < FRAME_CENTER[0]:
            object_last_position = "left"
        else:
            object_last_position = "right"
            
        logging.info(f"Object last seen {object_last_position} because the center of the object was {object_x_center.item()} and our frame center was {FRAME_CENTER[0]}")        

        logging.info(f"{TARGET_OBJECT} detected at ({object_x_center.item()}, {object_y_center.item()})\nOn the {object_last_position} side: Object center={object_x_center.item()} : Frame center = {FRAME_CENTER[0]} \nIt had area {round(object_area.item(), 0)}/ {TOTAL_CAMERA_AREA} = {round(object_area.item() / TOTAL_CAMERA_AREA,2)}")

        # If the object doesn't take up enough of the camera, move forward
        if target_object_coverage < OBJECT_TARGET_COVERAGE:
            tello.move_forward(20)
            logging.info(f"{target_object_coverage} < {OBJECT_TARGET_COVERAGE}: Moving forward")
        
        # If the object takes up too much of the camera, move back
        elif target_object_coverage >  1.3 * OBJECT_TARGET_COVERAGE:
            tello.move_back(20)
            logging.info(f"{target_object_coverage} > { round(1.3 * OBJECT_TARGET_COVERAGE, 2)}: Moving backward")
        
        # If the object is in the sweetspot, log it
        else:
            logging.info(f"Target object in the sweetspot: {OBJECT_TARGET_COVERAGE} < {target_object_coverage} < {round(1.3 * OBJECT_TARGET_COVERAGE, 2)}")

# Cleanup
tello.streamoff()
cv2.destroyAllWindows()
tello.land()
