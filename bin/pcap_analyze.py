import os
import sys
import argparse
import warnings

# Suppress potential DeprecationWarnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

sys.path.insert(1, os.path.join(os.path.dirname(__file__), '../utils'))
from input_processor import process_input
from subprocess_utils import execute_script

def is_pcap_file(file_path):
    # Check if the file has a .pcap or .pcapng extension
    return file_path.lower().endswith(('.pcap', '.pcapng'))

def analyze_pcap(file_path, verbose):
    if not is_pcap_file(file_path):
        print(f"Error: {file_path} is not a PCAP file.")
        return None, [f"Error: {file_path} is not a PCAP file."]

    bin_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(bin_dir) # ADFTool root folder, /home/bryan/Documents/ADFTool
    modules_dir = os.path.join(root_dir, "modules")
    result_dir = os.path.join(os.path.dirname(modules_dir), "results", f"results_{os.path.basename(file_path)}")

    progress_messages = []
    subprocesses = []

    print(f"Analyzing {file_path} with packet capture analysis...")

    # The path to the script
    pcap_script = os.path.join(modules_dir, "pcap_analysis.sh")
    
    process, message = execute_script(pcap_script, file_path, result_dir, verbose)
    subprocesses.append(process)
    progress_messages.append(message)

    for subprocess_obj in subprocesses:
        subprocess_obj.wait()
        stdout, stderr = subprocess_obj.communicate()
        if subprocess_obj.returncode == 0:
            progress_messages.append(f"{subprocess_obj.args[0]} analysis completed successfully.")
        else:
            progress_messages.append(f"Error executing {subprocess_obj.args[0]} script:\nReturn code: {subprocess_obj.returncode}\nOutput: {stderr}")

    progress_messages.append("PCAP analysis script completed.")

    return subprocesses, progress_messages

def process_input_wrapper(input_path, analyze_func, verbose):
    if os.path.isfile(input_path):
        if is_pcap_file(input_path):
            return process_input(input_path, analyze_func, verbose)
        else:
            print(f"Error: {input_path} is not a PCAP file.")
            return None
    elif os.path.isdir(input_path):
        results = []
        for root, _, files in os.walk(input_path):
            for file in files:
                file_path = os.path.join(root, file)
                if is_pcap_file(file_path):
                    result = process_input(file_path, analyze_func, verbose)
                    if result:
                        results.append(result)
                else:
                    print(f"Skipping {file_path}: Not a PCAP file.")
        return results
    else:
        print(f"Error: {input_path} is not a valid file or directory.")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze PCAP files.')
    parser.add_argument('input_path', help='PCAP file or directory path')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    process_input_wrapper(args.input_path, analyze_pcap, args.verbose)