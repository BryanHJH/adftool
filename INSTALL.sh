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

# Run the Docker container
echo "Running the Docker container..."
docker run -d -p 5001:5001 --name adftool-container adftool

# Check if the container is running
if [ $(docker ps -q -f name=adftool-container) ]; then
    echo "ADFTool is now running on http://localhost:5001"
else
    echo "Failed to start the ADFTool container."
    exit 1
fi