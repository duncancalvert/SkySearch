import cv2
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoHTMLAttributes
import numpy as np
import av
from PIL import Image
import os
import shutil
import torch


# --- How to interact with this application in the terminal:
# Start: streamlit run .../streamlit_app.py
# End: ctrl + d


st.set_page_config(layout="wide")


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

    # --- Base page configurations
    st.title("SkySearch Ground Control")

    # --- Turn on the webcam
    webrtc_streamer(
        key="streamer",
        sendback_audio=False
    )
    st.sidebar.title('Settings')

    # --- Buttons
    st.sidebar.header('Commands')
    col1, col2, col3 = st.columns(3)
    take_off_button = st.sidebar.button("Take Off")
    flip_button = st.sidebar.button("Flip")
    circle_button = st.sidebar.button("Circle")

    # --- Facial recognition accuracy slider
    st.sidebar.header('Optimizers')
    facial_rec_slider = st.sidebar.slider('Facial Recognition Confidence Threshold ', 0, 100, 25)

    # --- CoCo names selection
    option = st.sidebar.multiselect(
        'What would you like to find?',
        ('Blue', 'Red', 'Green'))

    # --- File uploader
    uploaded_file = st.sidebar.file_uploader("Upload an image of what you're trying to find", type=["png", "jpg", "jpeg", "txt", "csv", "pdf", "docx", "xlsx"])
    if uploaded_file is not None:
        # Specify the directory where the file will be saved
        save_directory = "SkySearch_UAV/.config/git/ignore/data/uploaded_data/"

        # Save the uploaded file
        file_path = save_uploaded_file(uploaded_file, save_directory)

        st.success(f"File '{uploaded_file.name}' saved to '{file_path}'")


# Run the Streamlit app
if __name__ == "__main__":
    main()