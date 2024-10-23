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
        credentials = service_account.Credentials.from_service_account_file(path_to_config)
        PROJECT_ID = "cocos-1682214059888"
        LOCATION = "us-central1"
        vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=credentials)

    
    def api_request(self, prompt, image, model = "gemini-1.5-pro"):
        
        model = GenerativeModel("gemini-1.5-pro")
        contents = [image, prompt]
        response = model.generate_content(contents)
        return response.text

if __name__ == "__main__":
    pass