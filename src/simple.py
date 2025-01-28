import time
import logging
import cv2
import matplotlib.pyplot as plt
from UAV import UAV
from LLM import LLM
from LLM import Info

logging.basicConfig(filename='drone.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('UAVLogger')

def main():
    # Initialize UAV and LLM
    drone_ip = "10.0.0.179"

    if drone_ip is None:
        uav = UAV()
    else:
        uav = UAV(drone_ip)
    uav.connect()

    # Initialize rotation tracking
    current_rotation = 0  # Degrees
    last_seen_rotation = None  # Stores the rotation where the object was last seen

    # LLM Initialization
    info = Info()
    llm = LLM(info.API_KEY, info.ORGANIZATION, info.PROJECT, None)


    # Stream and take off
    uav.streamon()
    uav.takeoff(reason="Looking for object using LLM")
    description = "person"

    prompt_lr = f"""
    Please provide the object's location within the image based on this description: {description}.
    You have 3 options for the left-right axis: left, center, right.
    Only respond with one word: 'left', 'center', or 'right'.
    If the object is not present, respond with 'not'.
    """

    prompt_nf = f"""
    Please provide the object's location within the image based on this description: {description}.
    You have 3 options for the near to far axis: near, medium, or far
    Only respond with one word: 'near', 'medium' or 'far'
    """

    # Matplotlib setup for live display
    plt.ion()  # Turn on interactive mode
    fig, ax = plt.subplots()
    img_display = ax.imshow(cv2.cvtColor(uav.get_frame_read().frame, cv2.COLOR_BGR2RGB))
    ax.axis("off")  # Hide axes

    searching = True
    while searching:
        try:
            # Get the camera feed
            image = uav.get_frame_read().frame
            
            image_rgb = image[:, :, ::-1]  # Reverse the last axis to convert BGR to RGB

            # Update Matplotlib display
            img_display.set_data(cv2.cvtColor(image_rgb, cv2.COLOR_BGR2RGB))
            plt.draw()
            plt.pause(0.001)  # Small pause to update the display

            # Query the LLM for the object's location
            processed_image = llm._process_image(image)
            response = llm.api_request(prompt_lr, processed_image, model="gpt-4o")

            logger.info(f"LLM response: {response}")
            print(f"LLM response: {response}")

            # Handle response
            if response == 'left':
                uav.rotate_counter_clockwise(20, reason="Object detected on the left")
                current_rotation = (current_rotation - 20) % 360
                last_seen_rotation = current_rotation  # Update last seen rotation
            elif response == 'right':
                uav.rotate_clockwise(20, reason="Object detected on the right")
                current_rotation = (current_rotation + 20) % 360
                last_seen_rotation = current_rotation  # Update last seen rotation
            elif response == 'not':
                logger.info("Object not detected, searching around last known position")
                if last_seen_rotation is not None:
                    # Calculate angular difference
                    angular_difference = (last_seen_rotation - current_rotation) % 360
                    if angular_difference > 180:
                        # Rotate counter-clockwise
                        uav.rotate_counter_clockwise(20, reason="Returning to last seen position (CCW)")
                        current_rotation = (current_rotation - 20) % 360
                    else:
                        # Rotate clockwise
                        uav.rotate_clockwise(20, reason="Returning to last seen position (CW)")
                        current_rotation = (current_rotation + 20) % 360
                else:
                    # Default search pattern if no last position is available
                    uav.rotate_clockwise(20, reason="Searching for object")
                    current_rotation = (current_rotation + 20) % 360
            elif response == 'center':
                logger.info("Object detected in the center")
                print("Object detected at center")
                last_seen_rotation = current_rotation  # Update last seen rotation

                # Query the LLM for near or far
                processed_image = llm._process_image(image)
                response_nf = llm.api_request(prompt_nf, processed_image, model="gpt-4o")
                logger.info(f"LLM near/far response: {response_nf}")
                print(f"LLM near/far response: {response_nf}")

                if response_nf == 'near':
                    uav.move('b', 20, reason="Moving backward to adjust distance")
                elif response_nf == 'far':
                    uav.move('f', 20, reason="Moving forward to adjust distance")
                else:
                    print('Perfectly centered and at optimal distance')
                    reason = "Goal Found!"
                    uav.flip('b', reason=reason)
                    time.sleep(.2)
                    uav.land(reason)
                    searching = False
            else:
                logger.warning(f"Unexpected response: {response}")

            time.sleep(0.5)  # Small delay between LLM queries

        except KeyboardInterrupt:
            print("Exiting...")
            logger.info("Script interrupted by user")
            break
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            break

    # Land the UAV after completion
    uav.land(reason="Task complete")
    plt.close()  # Close the Matplotlib window

if __name__ == "__main__":
    main()
