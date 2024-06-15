import os
import subprocess
import argparse

import sys
# Required to be able to import files from other folders
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '../src'))
from pyMagicBytes import FileObject

def analyze_file(file_path, verbose):

    # Directories
    bin_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(bin_dir) # ADFTool root folder, /home/bryan/Documents/ADFTool
    script_dir = os.path.join(root_dir, "scripts")
    result_dir = os.path.join(os.path.dirname(script_dir), "results", f"results_{os.path.basename(file_path)}")
    
    os.makedirs(result_dir, exist_ok=True)
    
    print(f"Analyzing {file_path} with steganalysis...")

    # The path to the scripts
    outguess_script = os.path.join(script_dir, "outguess_analysis.sh")
    stegoveritas_script = os.path.join(script_dir, "stegoveritas_analysis.sh")
    zsteg_script = os.path.join(script_dir, "zsteg_analysis.sh")
    binwalk_script = os.path.join(script_dir, "binwalk_analysis.sh")

    progress_messages = []
    subprocesses = []
    
    try:
        outguess_process = subprocess.Popen([outguess_script, file_path, result_dir, "-v" if verbose else ""], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        subprocesses.append(outguess_process)
        progress_messages.append("Outguess analysis started.")
    except subprocess.CalledProcessError as e:
        error_message = f"Error executing Outguess script: {str(e)}\nReturn code: {e.returncode}\nOutput: {e.output}"
        progress_messages.append(error_message)
        raise
    
    try:
        stegoveritas_process = subprocess.Popen([stegoveritas_script, file_path, result_dir, "-v" if verbose else ""], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        subprocesses.append(stegoveritas_process)
        progress_messages.append("Stegoveritas analysis started.")
    except subprocess.CalledProcessError as e:
        error_message = f"Error executing Stegoveritas script: {str(e)}\nReturn code: {e.returncode}\nOutput: {e.output}"
        progress_messages.append(error_message)
        raise
    
    try:
        zsteg_process = subprocess.Popen([zsteg_script, file_path, result_dir, "-v" if verbose else ""], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        subprocesses.append(zsteg_process)
        progress_messages.append("Zsteg analysis started.")
    except subprocess.CalledProcessError as e:
        error_message = f"Error executing Zsteg script: {str(e)}\nReturn code: {e.returncode}\nOutput: {e.output}"
        progress_messages.append(error_message)
        raise
    
    try:
        binwalk_process = subprocess.Popen([binwalk_script, file_path, result_dir, "-v" if verbose else ""], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        subprocesses.append(binwalk_process)
        progress_messages.append("Binwalk analysis started.")
    except subprocess.CalledProcessError as e:
        error_message = f"Error executing Binwalk script: {str(e)}\nReturn code: {e.returncode}\nOutput: {e.output}"
        progress_messages.append(error_message)
        raise
    
    for subprocess_obj in subprocesses:
        subprocess_obj.wait()
        stdout, stderr = subprocess_obj.communicate()
        if subprocess_obj.returncode == 0:
            progress_messages.append(f"{subprocess_obj.args[0]} analysis completed successfully.")
        else:
            progress_messages.append(f"Error executing {subprocess_obj.args[0]} script:\nReturn code: {subprocess_obj.returncode}\nOutput: {stderr}")
    
    progress_messages.append("All steganalysis scripts completed.")
    
    return subprocesses, progress_messages

def process_input(input_path, verbose):
    input_path = os.path.abspath(input_path)  # Convert to absolute path

    if os.path.isfile(input_path):
        analyze_file(input_path, verbose)
    elif os.path.isdir(input_path):
        for root, dirs, files in os.walk(input_path):
            for file in files:
                file_path = os.path.join(root, file)
                analyze_file(file_path, verbose)
    else:
        print(f"Invalid input: {input_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze files for steganalysis.')
    parser.add_argument('input_path', help='File or directory path')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    process_input(args.input_path, args.verbose)