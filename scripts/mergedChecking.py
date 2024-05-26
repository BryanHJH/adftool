import os
import json
import subprocess
from constants import SIGNATURES

def get_file_signature(file_path, max_bytes=32):
    with open(file_path, 'rb') as f:
        header = f.read(max_bytes)
    return header

def find_closest_signature(header):
    closest_sig = None
    min_diff = float('inf')
    for sig_dict in SIGNATURES:
        sig_bytes = bytes([b for b in sig_dict['hex'] if b is not None])
        if len(header) >= len(sig_bytes):
            diff = sum(a != b for a, b in zip(header, sig_bytes))
            if diff < min_diff:
                min_diff = diff
                closest_sig = sig_dict
    return closest_sig

def check_file_signature(file_path):
    file_ext = os.path.splitext(file_path)[1][1:].lower()
    header = get_file_signature(file_path)

    if file_ext in ['pcap', 'pcapng']:
        return True, {'file_extension': file_ext, 'description': 'Network packet capture'}, header

    for sig_dict in SIGNATURES:
        sig_bytes = bytes([b for b in sig_dict['hex'] if b is not None])
        if header[:len(sig_bytes)] == sig_bytes:
            return True, sig_dict, header

    return False, find_closest_signature(header), header

def analyze_file(file_path):
    is_match, sig_dict, header = check_file_signature(file_path)

    if is_match:
        if sig_dict['file_extension'] in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'pcap', 'pcapng']:
            print(f"Analyzing {file_path} with steganalysis and packet capture analysis...")
            result_dir = f"../results/results_{os.path.basename(file_path)}"
            os.makedirs(result_dir, exist_ok=True)
            subprocess.run(['./analysis.sh', file_path, result_dir], check=True)
        else:
            print(f"{file_path} is a {sig_dict['description']} file.")
    else:
        if sig_dict:
            print(f"{file_path} has an unexpected signature.")
            print(f"Expected signature for {sig_dict['file_extension']}: {sig_dict['hex']}")
            print(f"File's current signature: {list(header)}")
            expected_extension = find_closest_signature(header)['file_extension']
            print(f"This file should be using the {expected_extension} file extension based on its signature.")
        else:
            print(f"{file_path} has an unknown file signature.")

def process_input(input_path):
    input_path = os.path.abspath(input_path)  # Convert to absolute path

    if os.path.isfile(input_path):
        analyze_file(input_path)
    elif os.path.isdir(input_path):
        for root, dirs, files in os.walk(input_path):
            for file in files:
                file_path = os.path.join(root, file)
                analyze_file(file_path)
    else:
        print(f"Invalid input: {input_path}")

if __name__ == "__main__":
    input_path = input("Enter the file or directory path: ")
    process_input(input_path)
