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
	if command == "fly." and not flying:
		print("Taking off...")
		flying = True
		tello.takeoff()
	elif command == "land." and flying:
		print("Landing...")
		flying = False
		tello.land()
	elif command == "forward.":
		print("Going forward...")
		tello.move_forward(100)
	elif command == "back.":
		print("Going back...")
		tello.move_back(100)
	elif command == "up.":
		print("Going to up...")
		tello.move_up(30)
	elif command == "down.":
		print("Going to down...")
		tello.move_down(30)
	elif command == "flip.":
		print("Going to flip forward...")
		tello.flip_forward()
	elif command == "grip.":
		print("Going to flip forward...")
		tello.flip_back()
	elif command == "chip.":
		print("Going to flip right...")
		tello.flip_right()
	elif command == "back.":
		print("Going back...")
		tello.move_back(100)
	# other commands
	elif command == "stop.":
		tello.stop()
	elif command == "end.":
		print("Ending...")
		break

time.sleep(1)
tello.land()
tello.end()