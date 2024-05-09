import streamlit as st
import os
import shutil


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
