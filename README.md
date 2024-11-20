<picture align="left">
  <source media="(prefers-color-scheme: dark)" srcset="media/images/SkySearch_Logos/SkySearchLogo5_WithText.png">
  <img alt="SkySearch Logo" src="media/images/SkySearch_Logos/SkySearchLogo5_WithText.png">
</picture>

-------------
# SkySearch: Missing Person Identification Using Aerial Drone Sensing
UChicago Robotics Capstone December 2024


|||
| --- | --- |
| Authors | Duncan Calvert, Joon Park, Zach Farahany, Mohammad Ayan Raheel|
| Package | [![PyPI Latest Release](https://img.shields.io/pypi/v/pandas.svg)](https://pypi.org)|
| Meta | [License - MIT](https://github.com/DonutsDuncan/SkySearch_UAV/blob/main/LICENSE)|

## What is it?

**SkySearch** is an open source Python package that allows simple, flexible, and robust DJI drone swarm capabilities tailored for search and rescue. Specifically, it provides a command center UI layer, flight controls, AI modeling extensibility, and speech-to-text for drone commands. SkySearch allows emergency personnel to search based on a single photo of a lost person as well as a textual description. This project was initialized as part of the University of Chicago's M.S. in Applied Data Science Capstone 2024.

## Table of Contents

- [Main Features](#main-features)
- [Where to get it](#where-to-get-it)
- [License](#license)
- [Documentation and User Guide](#documentation)

## Main Features

* <ins>Ground Control Station (GCS)</ins>: The GCS serves as the central hub for mission planning, monitoring, and flight control. It includes a user-friendly interface for defining search areas, setting flight parameters, and receiving real-time updates from the drone swarm.
* <ins>Drone Swarm</ins>: The swarm comprises of multiple UAVs equipped with high-resolution cameras, GPS, and onboard processing units. The drones communicate with each other and the GCS to coordinate their search patterns and share information.
* <ins>Image Recognition/Text-to-Image Matching</ins>: This module is responsible for generating images based on a textual description of the missing person or accepting uploaded photos. The module then compares these reference images against the real-time drone video feeds. Advanced computer vision techniques, such as convolutional neural networks (CNNs), YOLO, and FaceNet are employed for face detection and recognition. 

## Where to get it

Check back soon! SkySearch will be made available via PyPI and Streamlit Cloud in the next few months.

## License

SkySearch is published under the [MIT License](https://github.com/DonutsDuncan/SkySearch_UAV/blob/main/LICENSE)

## Documentation

The SkySearch UI is meant to be a simple and intutitve experience for users of all skill levels. 
* Users can cycle through the various drone swarm functions via the Settings menu on the left.
* To connect a drone, please follow the steps outlined in the Drone on Private python file


