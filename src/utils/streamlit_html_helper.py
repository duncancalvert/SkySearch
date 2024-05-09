import streamlit as st
import os


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