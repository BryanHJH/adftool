import os
import subprocess
import argparse

def analyze_pcap(file_path, verbose):
    bin_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(bin_dir) # ADFTool root folder, /home/bryan/Documents/ADFTool
    script_dir = os.path.join(root_dir, "scripts")
    result_dir = os.path.join(os.path.dirname(script_dir), "results", f"results_{os.path.basename(file_path)}")

    progress_messages = []
    subprocesses = []

    print(f"Analyzing {file_path} with packet capture analysis...")

    # The path to the script
    pcap_script = os.path.join(script_dir, "pcap_analysis.sh")
    
    try:
        pcap_process = subprocess.Popen([pcap_script, file_path, result_dir, "-v" if verbose else ""], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        subprocesses.append(pcap_process)
        progress_messages.append("PCAP analysis started.")
    except subprocess.CalledProcessError as e:
        error_message = f"Error executing PCAP analysis script: {str(e)}\nReturn code: {e.returncode}\nOutput: {e.output}"
        progress_messages.append(error_message)
        raise

    for subprocess_obj in subprocesses:
        subprocess_obj.wait()
        stdout, stderr = subprocess_obj.communicate()
        if subprocess_obj.returncode == 0:
            progress_messages.append(f"{subprocess_obj.args[0]} analysis completed successfully.")
        else:
            progress_messages.append(f"Error executing {subprocess_obj.args[0]} script:\nReturn code: {subprocess_obj.returncode}\nOutput: {stderr}")

    progress_messages.append("PCAP analysis script completed.")

    return subprocesses, progress_messages

def process_input(input_path, verbose):
    input_path = os.path.abspath(input_path)  # Convert to absolute path

    if os.path.isfile(input_path):
        analyze_pcap(input_path, verbose)
    elif os.path.isdir(input_path):
        for root, dirs, files in os.walk(input_path):
            for file in files:
                file_path = os.path.join(root, file)
                analyze_pcap(file_path, verbose)
    else:
        print(f"Invalid input: {input_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze PCAP files.')
    parser.add_argument('input_path', help='File or directory path')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    process_input(args.input_path, args.verbose)