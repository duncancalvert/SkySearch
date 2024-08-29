from djitellopy import Tello

"""
    1. Connect to the drone locally
    2. Run the script to tell it which wifi to connect to. Drone will reboot
    3. Connect your laptop to "drone"
    4. Launch Angry IP and use the MAC address to find your drone
    5. Copy your IP address and put it in your code
"""

wifi_name = "OUR2.4"
wifi_password = "ZachAlex12"

# Connect to the drone
drone = Tello()
drone.connect()

# Connect to your home WiFi
drone.connect_to_wifi(wifi_name,wifi_password)

# reboot the drone
drone.reboot()
