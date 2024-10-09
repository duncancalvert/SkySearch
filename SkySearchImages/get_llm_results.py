import os
import cv2
import sys
import pandas as pd

excel_filename = "SkySearch Images.xlsx"
excel_file = pd.read_excel(excel_filename)
column = 'ChatGPT 4o prediction3'
excel_file[column] = ''

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
    llm = LLM(info.API_KEY, info.ORGANIZATION, info.PROJECT)

    # Get the directory of the current file
    current_dir = os.path.dirname(__file__)
    
    # Get all image files in the current directory
    image_files = [os.path.join(current_dir, f) for f in os.listdir(current_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    # Sort image files based on the number within the name
    image_files.sort(key=lambda x: int(''.join(filter(str.isdigit, os.path.basename(x)))))
    
    # For demonstration, let's just use the first image
    if image_files:
        image_path = image_files[0]
        image = cv2.imread(image_path)
    else:
        print("No image files found in the current directory.")

    for image_path in image_files:
        image_file_name = os.path.basename(image_path)

        try:
            image = cv2.imread(image_path)
            processed_image = llm._process_image(image)
            
            print(f"Reading {image_file_name}")

            selected_row = excel_file[excel_file['Image File name'] == image_file_name]
            description = selected_row['Item in image']
            # description = input("Enter a brief description of the object: ")
            prompt = f"""
                Please locate the object within the image based on the following description: {description}

Instructions:

	•	Horizontal Position: Select one word to describe the object’s position from left to right:
	•	left
	•	center
	•	right
	•	Vertical Position: Select one word to describe the object’s position from top to bottom:
	•	top
	•	center
	•	bottom
	•	Depth: Select one word to describe how close the object appears:
	•	near
	•	medium
	•	far

Your response should:

	•	Consist of exactly three words, one from each category above.
	•	Exclude any additional words, punctuation, or capitalization."""
            response = llm.api_request(prompt, processed_image, model = "gpt-4o")
            message = response['choices'][0]['message']['content']
            excel_file.loc[excel_file['Image File name'] == image_file_name, column] = message
        except:
            print(f"Failure encountered for {image_file_name}")
    
    print("Done")

    excel_file.to_excel(excel_filename)

    
if __name__ == "__main__":
    print("Executing main")
    main()
    print("Executed main")