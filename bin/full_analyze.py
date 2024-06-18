import os
import argparse
import sys

# Required to be able to import files from other folders
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '../modules'))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '../utils'))
from magic_byte_analysis import check_file_signature, analyze_file as analyze_file_magic_bytes
from image_analyze import analyze_file as analyze_image_file
from pcap_analyze import analyze_pcap
from input_processor import process_input

def analyze_file(file_path, verbose):  # sourcery skip: extract-method
    is_match, sig_dict = check_file_signature(file_path)
    
    if is_match:
        bin_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(bin_dir) # ADFTool root folder, /home/bryan/Documents/ADFTool
        modules_dir = os.path.join(root_dir, "modules")
        result_dir = os.path.join(os.path.dirname(modules_dir), "results", f"results_{os.path.basename(file_path)}")
        
        os.makedirs(result_dir, exist_ok=True)
        
        if sig_dict['file_extension'] in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
            analyze_image_file(file_path, verbose)
        elif sig_dict['file_extension'] in ['pcap', 'pcapng']:
            analyze_pcap(file_path, verbose)
        else:
            is_match, signature_message, magic_bytes_message, file_extension, has_extension = analyze_file_magic_bytes(file_path, verbose)
            
            if not is_match:
                print(signature_message)
                print(magic_bytes_message)
    else:
        is_match, signature_message, magic_bytes_message, file_extension, has_extension = analyze_file_magic_bytes(file_path, verbose)
        
        if not is_match:
            print(signature_message)
            print(magic_bytes_message)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze files for steganalysis and packet capture.')
    parser.add_argument('input_path', help='File or directory path')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    process_input(args.input_path, analyze_file, args.verbose)