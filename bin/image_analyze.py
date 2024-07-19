import os
import sys
import argparse
import warnings

# Suppress the DeprecationWarning for imghdr
warnings.filterwarnings("ignore", category=DeprecationWarning)
import imghdr

# Required to be able to import files from other folders
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '../utils'))
from input_processor import process_input
from subprocess_utils import execute_script

def is_image_file(file_path):
    return imghdr.what(file_path) is not None

def analyze_file(file_path, verbose):
    if not is_image_file(file_path):
        print(f"Error: {file_path} is not an image file.")
        return None, [f"Error: {file_path} is not an image file."]

    # Directories
    bin_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(bin_dir) # ADFTool root folder, /home/bryan/Documents/ADFTool
    modules_dir = os.path.join(root_dir, "modules")
    result_dir = os.path.join(os.path.dirname(modules_dir), "results", f"results_{os.path.basename(file_path)}")
    
    os.makedirs(result_dir, exist_ok=True)
    
    print(f"Analyzing {file_path} with steganalysis...")

    # The path to the scripts
    script_paths = [
        os.path.join(modules_dir, "outguess_analysis.sh"),
        os.path.join(modules_dir, "stegoveritas_analysis.sh"),
        os.path.join(modules_dir, "zsteg_analysis.sh"),
        os.path.join(modules_dir, "binwalk_analysis.sh")
    ]

    progress_messages = []
    subprocesses = []
    
    for script_path in script_paths:
        process, message = execute_script(script_path, file_path, result_dir, verbose)
        subprocesses.append(process)
        progress_messages.append(message)
    
    for subprocess_obj in subprocesses:
        subprocess_obj.wait()
        stdout, stderr = subprocess_obj.communicate()
        if subprocess_obj.returncode == 0:
            progress_messages.append(f"{subprocess_obj.args[0]} analysis completed successfully.")
        else:
            progress_messages.append(f"Error executing {subprocess_obj.args[0]} script:\nReturn code: {subprocess_obj.returncode}\nOutput: {stderr}")
    
    progress_messages.append("All steganalysis scripts completed.")
    
    return subprocesses, progress_messages

def process_input_wrapper(input_path, analyze_func, verbose):
    if os.path.isfile(input_path):
        if is_image_file(input_path):
            return process_input(input_path, analyze_func, verbose)
        else:
            print(f"Error: {input_path} is not an image file.")
            return None
    elif os.path.isdir(input_path):
        results = []
        for root, _, files in os.walk(input_path):
            for file in files:
                file_path = os.path.join(root, file)
                if is_image_file(file_path):
                    result = process_input(file_path, analyze_func, verbose)
                    if result:
                        results.append(result)
                else:
                    print(f"Skipping {file_path}: Not an image file.")
        return results
    else:
        print(f"Error: {input_path} is not a valid file or directory.")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze image files for steganalysis.')
    parser.add_argument('input_path', help='Image file or directory path')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    process_input_wrapper(args.input_path, analyze_file, args.verbose)