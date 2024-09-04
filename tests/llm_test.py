import os
import cv2
import sys

# Make the current working directory the directory above so that we can call our source python files
def add_to_path(path:str) -> None:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), path)))
    
add_to_path("..")
add_to_path("../src")


from src.LLM import LLM
from src.LLM import Info

info = Info()

def show_image(image):
        """
        Displays the captured image in a window.
        Args:
            image (Array): The image to display.
        """
        cv2.imshow('Captured Image', image)
        cv2.waitKey(0)  # Wait for a key press to close the window
        cv2.destroyAllWindows()

def main():
    llm = LLM(info.API_KEY, info.ORGANIZTION, info.PROJECT)

    image = llm.get_test_image()
    show_image(image)
    processed_image = llm._process_image(image)
    description = "Adult male"
    prompt = f"""
        Tell me where this object is within the image. Here is a brief description of it: {description}.
        You will have 3 options for the left-right axis and 3 for the vertical axis. In addition, you can tell me if it appears near medium or far. Options: left, center, right. top, center, bottom. near, medium, far.
        Only respond with these 3 words, no punctuation or capitalization.
    """
    
    response = llm.api_request(prompt, processed_image)
    print(response)



    
if __name__ == "__main__":
    print("Executing main")
    main()
    print("Executed main")