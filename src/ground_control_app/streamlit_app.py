import cv2
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoHTMLAttributes
import numpy as np
import av
from PIL import Image
import os
import shutil
import torch
import yaml


# --- How to interact with this application in the terminal:
# Start: streamlit run .../streamlit_app.py
# End: ctrl + d


st.set_page_config(layout="wide")


# Define a function to center the title
def centered_title(title):
    # Use custom CSS to center the title
    st.markdown(
        f"""
        <style>
        .centered-title {{
            text-align: center;
            font-size: 3em;
            font-weight: bold;
        }}
        </style>
        <div class="centered-title">{title}</div>
        """,
        unsafe_allow_html=True,
    )


divider_css = """
<style>
.divider {
    height: 1px;
    width: 100%;
    background-color: #ddd;
    margin: 20px 0;
}
</style>
"""

def save_uploaded_file(uploaded_file, save_directory):
    """
    Save an uploaded file to a specified directory.

    Parameters:
    - uploaded_file: The uploaded file from Streamlit's file uploader.
    - save_directory: The directory where the file will be saved.
    :return: file path of saved file upload
    """
    # Check if the directory exists, if not, create it
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    # Create the file path where the file will be saved
    file_path = os.path.join(save_directory, uploaded_file.name)

    # Save the file
    with open(file_path, "wb") as f:
        shutil.copyfileobj(uploaded_file, f)

    return file_path


def load_model(path, device):
    model_ = torch.hub.load('ultralytics/yolov8', 'custom', path=path, force_reload=True)
    model_.to(device)
    print("model to ", device)
    return model_


def main():
    """
    Main page UI with calls to other subfunctions
    :return: page UI displayed on web browser
    """

    # --- Page Title
    centered_title("SkySearch Ground Control")

    # Create two equal sized columns
    col1, col2 = st.columns(2)

    # --- Turn on the webcam
    with col1:
        st.subheader('Drone camera feed')
        webrtc_streamer(
            key="streamer",
            sendback_audio=False
        )
        st.sidebar.title('Settings')

    with col2:
        st.subheader('Map')

    # Add a divider to the page
    st.markdown(divider_css, unsafe_allow_html=True)
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # Create two new columns below the divider
    col3, col4 = st.columns(2)

    with col3:
        st.subheader('Speech-to-Text Commands')

    # --- Buttons
    st.sidebar.header('Commands')
    take_off_button = st.sidebar.button("Take Off")
    flip_button = st.sidebar.button("Flip")
    circle_button = st.sidebar.button("Circle")

    # --- Facial recognition accuracy slider
    st.sidebar.header('Optimizers')
    facial_rec_slider = st.sidebar.slider('Confidence Threshold ', 0, 100, 25)

    # --- CoCo names selection
    with open("/Users/attis/PycharmProjects/SkySearch_UAV/SkySearch_UAV/ultralytics/ultralytics/cfg/datasets/coco8.yaml", "r") as file:
        coco_data = yaml.safe_load(file)

    # Grab all Coco Names from the YaML file
    coco_classes = coco_data.get('names')
    select_classes = st.sidebar.multiselect("Select COCO Classes for Analysis", coco_classes)

    # --- Image uploader/text description box
    radio_button_input = st.sidebar.radio("Would you like to search with an image or a textual description?", ["Image upload", "Text description"])
    # URL, upload file (max 200 mb)
    if radio_button_input == "Image upload":
        uploaded_file = st.sidebar.file_uploader("Upload an image of what you're trying to find", type=["png", "jpg", "jpeg", "txt", "csv", "pdf", "docx", "xlsx"])
        if uploaded_file is not None:
            # Specify the directory where the file will be saved
            save_directory = "SkySearch_UAV/.config/git/ignore/data/uploaded_data/"

            # Save the uploaded file
            file_path = save_uploaded_file(uploaded_file, save_directory)

            st.success(f"File '{uploaded_file.name}' saved to '{file_path}'")

    # Input for textual description of what you're trying to find
    if radio_button_input == "Text description":
        user_text = st.sidebar.text_area("Enter your text here", height=200)

        # Add a submit button to trigger the processing of the entered text
        submit_button = st.sidebar.button("Submit")

        if submit_button:
            if user_text:
                st.sidebar.write("You entered the following text:")
                st.sidebar.write(user_text)
            else:
                st.sidebar.warning("Please enter some text before submitting")


# Run the Streamlit app
if __name__ == "__main__":
    main()