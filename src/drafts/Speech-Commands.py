from djitellopy import Tello
import cv2
import azure.cognitiveservices.speech as speechsdk
import time

# flying = False
tello = Tello('192.168.87.22')
tello.connect()

speech_config = speechsdk.SpeechConfig(subscription="918d5b6e21fb4a57b45e3b23130d9ffb", endpoint="https://eastus2.api.cognitive.microsoft.com/sts/v1.0/issuetoken")
speech_config.speech_recognition_language="en-US"
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

# This will get our command from the speech recognizer
def get_command():
	try:
		result = speech_recognizer.recognize_once()
		if result.reason == speechsdk.ResultReason.RecognizedSpeech:
			print(f"Recognized: {result.text.lower()}")
			return result.text.lower()
		elif result.reason == speechsdk.ResultReason.NoMatch:
			print("No speech could be recognized")
			return None
	except Exception as e:
		print(f"Error in get_command: {e}")
		return None

# Handle all of our drone commands
def fly():
	if not flying:
		print("Taking off...")
		flying = True
		tello.takeoff()

def land():
	if flying:
		print("Landing...")
		flying = False
		tello.land()

def move_forward():
	print("Going forward...")
	tello.move_forward(100)

def move_back():
	print("Going back...")
	tello.move_back(100)

def move_up():
	print("Going up...")
	tello.move_up(30)

def move_down():
	print("Going down...")
	tello.move_down(30)

def flip_forward():
	print("Flipping forward...")
	tello.flip_forward()

def flip_back():
	print("Flipping back...")
	tello.flip_back()

def flip_right():
    print("Flipping right...")
    tello.flip_right()

def stop():
    tello.stop()

def end():
    print("Ending...")
    tello.land()
    tello.end()

if __name__ == "__main__":
    # This is just to get our drone running
    print("Say 'start' to begin.")
    while True:
        command = get_command()
        if command == "start.":
            print("Ready for commands...")
            break

    # Follow speech commands
    flying = False
    while True:
        print("Say a command...")
        input("Press Enter to continue...")
        command = get_command()
        
        # Process all of our commands
        if command:
            switcher = {
                "fly.": lambda: fly(),
                "land.": lambda: land(),
                "forward.": lambda: move_forward(),
                "back.": lambda: move_back(),
                "up.": lambda: move_up(),
                "down.": lambda: move_down(),
                "flip.": lambda: flip_forward(),
                "grip.": lambda: flip_back(),
                "chip.": lambda: flip_right(),
                "stop.": lambda: stop(),
                "end.": lambda: end()
            }
            func = switcher.get(command, lambda: print("Invalid command"))
            func()

