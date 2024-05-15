import streamlit as st
import os
import shutil
from streamlit_webrtc import webrtc_streamer, VideoHTMLAttributes


# Define a function to center the title
def centered_title(title):
    """
    Helper function to use customer CSS to center the streamlit title text
    :param title:
    :return:
    """
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
        unsafe_allow_html=True)


def html_divider():
    """
    Helper function to use customer CSS to add a page divider in streamlit
    :param N/A
    :return: N/A
    """
    st.markdown(
        f"""
        <style>
        .divider {{
            height: 1px;
            width: 100%;
            background-color: #ddd;
            margin: 20px 0;
        }}
        </style>
        """,
        unsafe_allow_html=True)
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)


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


def ground_control():
    """
        Main page UI with calls to other sub-functions
        :return: page UI displayed on web browser
        """

    st.set_page_config(layout="wide")

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

    html_divider()

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

    # --- Current Active Skill
    radio_button_current_active_skill = st.sidebar.radio("What skill would you like to use",
                                          ["Nothing", "Voice Commands", "Hand Signals", "Find Something"])

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
    select_coco_classes = st.sidebar.multiselect("Select COCO Classes for Analysis", coco_classes)

    # --- Image uploader/text description box
    radio_button_input = st.sidebar.radio("Would you like to search with an image or a textual description?",
                                          ["Image upload", "Text description"])
    # URL, upload file (max 200 mb)
    if radio_button_input == "Image upload":
        uploaded_file = st.sidebar.file_uploader("Upload an image of what you're trying to find",
                                                 type=["png", "jpg", "jpeg", "txt", "csv", "pdf", "docx", "xlsx"])
        if uploaded_file is not None:
            # Specify the directory where the file will be saved
            save_directory = ".config/git/ignore/data/uploaded_data"

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

    return facial_rec_slider, select_coco_classes, radio_button_current_active_skill
