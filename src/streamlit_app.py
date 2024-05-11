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
from utils import streamlit_html_helper


# --- How to interact with this application in the terminal:
# Start: streamlit run .../streamlit_app.py
# End: ctrl + d

st.set_page_config(layout="wide")


def load_model(path, device):
    model_ = torch.hub.load('ultralytics/yolov8', 'custom', path=path, force_reload=True)
    model_.to(device)
    print("model to ", device)
    return model_


def main():
    """
    Main page UI with calls to other sub-functions
    :return: page UI displayed on web browser
    """

    # --- Page Title
    streamlit_html_helper.centered_title("SkySearch Ground Control")

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

    streamlit_html_helper.html_divider()
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # Create two new columns below the divider
    col3, col4 = st.columns(2)

    with col3:
        st.subheader('Speech-to-Text Commands')

    with col4:
        st.subheader('Commands')
        # --- Buttons
        col5, col6, col7, col8 = st.columns(4)
        with col5:
            take_off_button = st.button("Take Off")
        with col6:
            flip_button = st.button("Land")
        with col7:
            circle_button = st.button("Flip")
        with col8:
            circle_button = st.button("Circle")

    # --- Facial recognition accuracy slider
    st.sidebar.header('Optimizers')
    facial_rec_slider = st.sidebar.slider('Confidence Threshold ', 0, 100, 25)

    # Display CoCo names in a selector
    coco_classes = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train",
                    "truck", "boat", "traffic light", "fire hydrant", "stop sign", "parking meter",
                    "bench", "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra",
                    "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis",
                    "snowboard", "sports ball", "kite", "baseball bat", "baseball glove", "skateboard",
                    "surfboard", "tennis racket", "bottle", "wine glass", "cup", "fork", "knife", "spoon",
                    "bowl", "banana", "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza",
                    "donut", "cake", "chair", "sofa", "pottedplant", "bed", "diningtable", "toilet", "tvmonitor",
                    "laptop", "mouse", "remote", "keyboard", "cell phone", "microwave", "oven", "toaster",
                    "sink", "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier",
                    "toothbrush"]
    select_classes = st.sidebar.multiselect("Select COCO Classes for Analysis", coco_classes)

    # --- Image uploader/text description box
    radio_button_input = st.sidebar.radio("Would you like to search with an image or a textual description?", ["Image upload", "Text description"])
    # URL, upload file (max 200 mb)
    if radio_button_input == "Image upload":
        uploaded_file = st.sidebar.file_uploader("Upload an image of what you're trying to find", type=["png", "jpg", "jpeg", "txt", "csv", "pdf", "docx", "xlsx"])
        if uploaded_file is not None:
            # Specify the directory where the file will be saved
            save_directory = ".config/git/ignore/data/uploaded_data"

            # Save the uploaded file
            file_path = streamlit_html_helper.save_uploaded_file(uploaded_file, save_directory)

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