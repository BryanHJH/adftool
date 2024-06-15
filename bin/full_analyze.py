import os
import subprocess
import filetype
import argparse
import shutil

import sys
# Required to be able to import files from other folders
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '../src'))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '../scripts'))
from pyMagicBytes import FileObject
from magic_byte_analysis import check_file_signature, compare_magic_bytes

def analyze_file(file_path, verbose):
    is_match, sig_dict = check_file_signature(file_path)
    
    if is_match:
        bin_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(bin_dir) # ADFTool root folder, /home/bryan/Documents/ADFTool
        script_dir = os.path.join(root_dir, "scripts")
        result_dir = os.path.join(os.path.dirname(script_dir), "results", f"results_{os.path.basename(file_path)}")
        
        os.makedirs(result_dir, exist_ok=True)
        
        if sig_dict['file_extension'] in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
            print(f"Analyzing {file_path} with steganalysis...")

            # The path to the scripts
            outguess_script = os.path.join(script_dir, "outguess_analysis.sh")
            stegoveritas_script = os.path.join(script_dir, "stegoveritas_analysis.sh")
            zsteg_script = os.path.join(script_dir, "zsteg_analysis.sh")
            binwalk_script = os.path.join(script_dir, "binwalk_analysis.sh")

            # Executing the scripts
            subprocess.run([outguess_script, file_path, result_dir, "-v" if verbose else ""], check=True)
            subprocess.run([stegoveritas_script, file_path, result_dir, "-v" if verbose else ""], check=True)
            subprocess.run([zsteg_script, file_path, result_dir, "-v" if verbose else ""], check=True)
            subprocess.run([binwalk_script, file_path, result_dir, "-v" if verbose else ""], check=True)
        elif sig_dict['file_extension'] in ['pcap', 'pcapng']:
            print(f"Analyzing {file_path} with packet capture analysis...")
            pcap_script = os.path.join(script_dir, "pcap_analysis.sh")
            subprocess.run([pcap_script, file_path, result_dir, "-v" if verbose else ""], check=True)
        else:
            guessed_type = filetype.guess(file_path)
        
            if guessed_type is not None:
                guessed_extension = guessed_type.extension
                print(f"{file_path} has no file extension. Guessed file type: {guessed_extension}")
                
                is_match, diff = compare_magic_bytes(file_path, guessed_extension)
                
                if is_match:
                    print(f"The magic bytes of {file_path} match the expected magic bytes for {guessed_extension} files.")
                    print(f"Rename the file to include the .{guessed_extension} extension.")
                else:
                    print(f"The magic bytes of {file_path} do not match the expected magic bytes for {guessed_extension} files.")
                    print(f"File's magic bytes: {diff[0]}")
                    print(f"Expected magic bytes: {diff[1]}")
                
                script_dir = os.path.dirname(os.path.abspath(__file__))
                result_dir = os.path.join(os.path.dirname(script_dir), "results", f"results_{os.path.basename(file_path)}")
                
                os.makedirs(result_dir, exist_ok=True)
                
                with open(os.path.join(result_dir, "magic_bytes_comparison.txt"), "w") as f:
                    if is_match:
                        f.write(f"The magic bytes of {file_path} match the expected magic bytes for {guessed_extension} files.\n")
                        f.write(f"Rename the file to include the .{guessed_extension} extension.\n")
                    else:
                        f.write(f"The magic bytes of {file_path} do not match the expected magic bytes for {guessed_extension} files.\n")
                        f.write(f"File's magic bytes: {diff[0]}\n")
                        f.write(f"Expected magic bytes: {diff[1]}\n")
                        
            else:
                print(f"{file_path} has an unknown file type.")
    else:
        print(f"{file_path} has an unknown file type.")

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
    parser = argparse.ArgumentParser(description='Analyze files for steganalysis and packet capture.')
    parser.add_argument('input_path', help='File or directory path')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    process_input(args.input_path, args.verbose)