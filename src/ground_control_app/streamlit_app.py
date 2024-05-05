import cv2
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoHTMLAttributes
import numpy as np
import av


def wide_space_default():
    """
    Set page default configurations
    """
    st.set_page_config(layout="wide")


# Start page with default configurations
wide_space_default()


st.title("SkySearch Ground Control")


# Turn on webcam
webrtc_streamer(
    key="streamer",
    sendback_audio=False
    )


# --- Buttons
st.sidebar.header('Commands')
col1, col2, col3 = st.columns(3)
take_off_button = st.sidebar.button("Take Off")
flip_button = st.sidebar.button("Flip")
circle_button = st.sidebar.button("Circle")


# --- Facial Recognition Accuracy Slider
st.sidebar.header('Thresholds')
facial_rec_slider = st.sidebar.slider('Facial Recognition Confidence Threshold ', 0, 100, 25)


# --- CoCo Names Selection
st.sidebar.header('CoCo Names Selections')
option = st.sidebar.multiselect(
     'What would you like to find?',
     ('Blue', 'Red', 'Green'))


# --- File Upload
st.sidebar.header('Photo Upload')
st.sidebar.file_uploader('Upload missing person picture here')


