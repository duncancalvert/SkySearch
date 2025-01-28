import os
import cv2
import sys
import pandas as pd

excel_filename = os.path.join(os.path.dirname(__file__), "Extended_Dataset.csv")

if excel_filename.endswith(".csv"):
    excel_file = pd.read_csv(excel_filename)
else:
    excel_file = pd.read_excel(excel_filename)
column = 'ChatGPT 4o prediction GLAD'
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
    
    response = llm.api_request("Hello how are you?", None, model="gpt-4o")
    print(response)

    # Get the directory of the current file
    current_dir = os.path.dirname(__file__)
    
    # Get the path to the Recognition Dataset directory
    recognition_dataset_dir = os.path.join(current_dir, "Recognition Data Set")
    
    # Get all image files in the Recognition Dataset directory
    image_files = [os.path.join(recognition_dataset_dir, f) for f in os.listdir(recognition_dataset_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
    
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
            
            print(f"Reading {image_file_name}")

            selected_row = excel_file[excel_file['Image File name'] == image_file_name]
            description = selected_row['Item in image']
            description = description.values[0]
            # description = input("Enter a brief description of the object: ")
            prompt = f"""Please provide the object’s location within the image based on this description: {description}. Use only these options for your response:

	•	Horizontal position: left, center, right
	•	Vertical position: top, center, bottom
	•	Depth: near, medium, far

Respond with exactly three words—one from each category—without punctuation or capitalization. If the item is not in the image, your response should be "not present" """,

            response = llm.api_request(prompt = prompt, image = image, model = "gpt-4o")
            message = response
            print(f"Response: {message}")
            excel_file.loc[excel_file['Image File name'] == image_file_name, column] = message
        except Exception as e:
            print(f"Failure encountered for {image_file_name}")
            raise e
    
    print("Done")
    if excel_filename.endswith(".csv"):
        excel_file.to_csv(excel_filename, index=False)
    else:
        excel_file.to_excel(excel_filename)

    
if __name__ == "__main__":
    print("Executing main")
    main()
    print("Executed main")