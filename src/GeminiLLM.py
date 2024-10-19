from google.cloud import aiplatform
from google.oauth2 import service_account
import vertexai
from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
    HarmBlockThreshold,
    HarmCategory,
    Image,
    Part,
    SafetySetting,
)
from PIL import Image as PIL_Image
from PIL import ImageOps as PIL_ImageOps

class GeminiLLM:
    def __init__(self, path_to_config):
        self.path_to_config = path_to_config
    
    def api_request(self, prompt, image, model = "gemini-1.5-pro"):
        
        model = GenerativeModel("gemini-1.5-pro")
        contents = [image, prompt]
        response = model.generate_content(contents)
        return response

if __name__ == "__main__":
    pass