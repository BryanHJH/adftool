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

rem Prompt the user for the folder path
set /p data_path="Enter the folder path that contains the files to be analysed: "
set /p result_path="Enter the folder path that will store the results: "

rem Check if the folder exists
if not exist "%data_path%" (
    echo The specified folder does not exist.
    exit /b 1
)

if not exist "%result_path%" (
    echo The specified folder does not exist.
    exit /b 1
)

rem Run the Docker container
echo Running the Docker container...
docker run -it -v %data_path%:/home/data -v %result_path%:/home/results adftool bash -c "source /home/.bashrc && bash"

rem Check if the container is running
docker ps -q -f name=adftool-container >nul 2>nul
if %errorlevel% equ 0 (
    echo ADFTool is now running
) else (
    echo Failed to start the ADFTool container.
    exit /b 1
)