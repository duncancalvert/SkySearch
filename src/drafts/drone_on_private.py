from djitellopy import Tello

"""
    1. Connect to the drone locally
    2. Run the script to tell it which wifi to connect to. Drone will reboot
    3. Connect your laptop to "drone"
    4. Launch Angry IP and use the MAC address to find your drone
    5. Copy your IP address and put it in your code
"""

# Connect to the drone
drone = Tello()
drone.connect()

# Connect to your home WiFi
drone.connect_to_wifi("drone", "Apple123!")

# reboot the drone
drone.reboot()
