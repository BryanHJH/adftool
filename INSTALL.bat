@echo off

rem Check if Docker is installed
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo Docker is not installed. Please install Docker and try again.
    exit /b 1
)

rem Build the Docker image
echo Building the Docker image...
docker build -t adftool .

rem Check if the build was successful
if %errorlevel% neq 0 (
    echo Failed to build the Docker image.
    exit /b 1
)

rem Run the Docker container
echo Running the Docker container...
docker run -d -p 5001:5001 adftool

rem Check if the container is running
docker ps -q -f name=adftool-container >nul 2>nul
if %errorlevel% equ 0 (
    echo ADFTool is now running on http://localhost:5001
) else (
    echo Failed to start the ADFTool container.
    exit /b 1
)