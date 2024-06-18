#!/bin/bash

# Check if Docker is installed
if ! command -v docker &> /dev/null
then
    echo "Docker is not installed. Please install Docker and try again."
    exit 1
fi

# Build the Docker image
echo "Building the Docker image..."
docker build -t adftool .

# Check if the build was successful
if [ $? -ne 0 ]; then
    echo "Failed to build the Docker image."
    exit 1
fi

# Prompt the user for the folder path
read -p "Enter the folder path that contains the files to be analysed: " data_path
read -p "Enter the folder path that will store the results: " result_path

# Check if the folders exist
if [ ! -d "$data_path" ]; then
    echo "The specified data folder does not exist."
    exit 1
fi

if [ ! -d "$result_path" ]; then
    echo "The specified result folder does not exist."
    exit 1
fi

# Run the Docker container
echo "Running the Docker container..."
docker run -it -v "$data_path":/home/data -v "$result_path":/home/results adftool bash

# Check if the container is running
if [ "$(docker ps -q -f name=adftool-container)" ]; then
    echo "ADFTool is now running."
else
    echo "Failed to start the ADFTool container."
    exit 1
fi