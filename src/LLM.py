import logging
import cv2
import base64
import requests
import time
import numpy as np
import io

class Info:
    def __init__(self, config_path: str = "config.txt") -> None:
        self.config = self._load_config(config_path)
        self.ORGANIZATION = self.config.get("ORGANIZATION")
        self.PROJECT = self.config.get("PROJECT")
        self.API_KEY = self.config.get("API_KEY")

    def _load_config(self, path: str):
        config = {}
        with open(path, 'r') as file:
            for line in file:
                key, value = line.strip().split('=')
                config[key] = value
        return config

logging.basicConfig(filename='drone.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('UAVLogger')

class LLM(object):
    def __init__(self, API_KEY, organization_id, project, path_to_gemini_configs = None) -> None:
        self.API_key = API_KEY
        self.organization_id = organization_id
        self.project = project
        self.path_to_gemini_configs = path_to_gemini_configs
    
    def get_test_image(self):
        """
        Captures an image from the computer's camera and returns it.
        Returns:
            image (Array): The captured image.
        """
        cap = cv2.VideoCapture(0)  # 0 is the default camera
        
        time.sleep(.5)

        if not cap.isOpened():
            logger.error("Could not open the camera for test image generation")
            raise Exception("Could not open the camera for test image generation")
            exit()

        ret, frame = cap.read()

        if not ret:
            logger.error("Failed to capture image from the camera during test image generation")
            raise Exception("Failed to capture image from the camera during test image generation")
            exit()
        
        cap.release()
        cv2.destroyAllWindows()
        
        logger.info("Test image successfully grabbed")
        return frame
    
    def _process_image(self, image):
        """
        Convert the input image to a base64-encoded string.
        Args:
            image (Array): This is the image that we want to process.
        Returns:
            processed_image (str): Base64-encoded image string.
        """
        _, buffer = cv2.imencode('.jpg', image)
        image_bytes = buffer.tobytes()
        processed_image = base64.b64encode(image_bytes).decode('utf-8')  # Base64 encode and decode to string
        return processed_image

    def api_request(self, prompt, image, model = "gpt-4o"): # TODO: Make it so that this returns just the response and nothing else, no other JSON stuff
        # TODO: Integrate with other gemini stuff
        
        if model in ["gpt-4o-mini", "gpt-4o"]:
            
        
            headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.API_key}"
                    }

            payload = {
                    "model":model,
                    "messages": [
                        {
                        "role": "user",
                        "content": [
                            {
                            "type": "text",
                            "text": prompt
                            },
                            {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image}",
                                "detail": "high" # <- We can change this so that the model gets a higher or lower resolution version of the image
                            }
                            }
                        ]
                        }
                    ],
                    "max_tokens": 300,
                    "temperature": 0.0 # Added temperature
                    }
            
            logger.info(f"LLM: Sending image to {model}")
            response = requests.post("https://api.openai.com/v1/chat/completions",
                                    headers = headers,
                                    json = payload
                                    )
            
            return response.json()['choices'][0]['message']['content']
        
        else: # Here we are using a Gemini Model
            self.GeminiLLM = GeminiLLM(self.path_to_gemini_configs)
            response = self.GeminiLLM.api_request(
                                      prompt = prompt,
                                      image = image,
                                      model = model
                                      )
            return response
        
if __name__ == "__main__":
    pass