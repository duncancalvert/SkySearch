#!/bin/bash

# This is meant to be run from the root directory of the project. Not from the setup folder or the src folder

# Navigate to the setup directory
cd setup

# Build the Docker image
echo "Building docker image"
docker-compose -f docker-compose.yml build

# Start the Docker container
echo "Starting docker container"
docker-compose -f docker-compose.yml up -d

echo "Development environment is up and running. You can start coding!"
