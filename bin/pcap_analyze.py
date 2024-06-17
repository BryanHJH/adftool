import os
import sys
import argparse

sys.path.insert(1, os.path.join(os.path.dirname(__file__), '../utils'))
from input_processor import process_input
from subprocess_utils import execute_script

def analyze_pcap(file_path, verbose):
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze PCAP files.')
    parser.add_argument('input_path', help='File or directory path')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    process_input(args.input_path, analyze_pcap, args.verbose)