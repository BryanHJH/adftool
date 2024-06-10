import os
import json
import subprocess
from pyMagicBytes import FileObject

def find_closest_signature(header):
    closest_sig = None
    min_diff = float('inf')
    for sig_dict in FileObject.allFileTypes:
        size, offset, magic_hex, ext, desc = sig_dict.strip().split('|')
        size = int(size)
        sig_bytes = bytes.fromhex(magic_hex)
        if len(header) >= len(sig_bytes):
            diff = sum(a != b for a, b in zip(header, sig_bytes))
            if diff < min_diff:
                min_diff = diff
                closest_sig = ext
    return closest_sig

def check_file_signature(file_path):
    try:
        file_obj = FileObject(file_path)
        possible_types = file_obj.getPossibleTypes()
        
        if len(possible_types) > 0:
            sig_dict = {
                'file_extension': possible_types[0][2][1],
                'description': possible_types[0][3][1]
            }
            return True, sig_dict
        else:
            return False, None
    except Exception as e:
        print(f"Error occurred while checking file signature: {str(e)}")
        return False, None

def analyze_file(file_path, verbose):
    is_match, sig_dict = check_file_signature(file_path)
    header = FileObject(file_path).fileStream.read(32)

    if is_match:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        result_dir = os.path.join(os.path.dirname(script_dir), "results", f"results_{os.path.basename(file_path)}")
        os.makedirs(result_dir, exist_ok=True)
        
        if sig_dict['file_extension'] in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
            print(f"Analyzing {file_path} with steganalysis...")
            outguess_script = os.path.join(script_dir, "outguess_analysis.sh")
            stegoveritas_script = os.path.join(script_dir, "stegoveritas_analysis.sh")
            zsteg_script = os.path.join(script_dir, "zsteg_analysis.sh")
            binwalk_script = os.path.join(script_dir, "binwalk.sh")
            subprocess.run([outguess_script, file_path, result_dir, "-v" if verbose else ""], check=True)
            subprocess.run([stegoveritas_script, file_path, result_dir, "-v" if verbose else ""], check=True)
            subprocess.run([zsteg_script, file_path, result_dir, "-v" if verbose else ""], check=True)
            subprocess.run([binwalk_script, file_path, result_dir, "-v" if verbose else ""], check=True)
        elif sig_dict['file_extension'] in ['pcap', 'pcapng']:
            print(f"Analyzing {file_path} with packet capture analysis...")
            pcap_script = os.path.join(script_dir, "pcap_analysis.sh")
            subprocess.run([pcap_script, file_path, result_dir, "-v" if verbose else ""], check=True)
        else:
            print(f"{file_path} is a {sig_dict['description']} file.")
    else:
        expected_extension = find_closest_signature(header)
        if expected_extension:
            print(f"{file_path} has an unknown file signature.")
            print(f"This file should be using the {expected_extension} file extension based on its signature.")
        else:
            print(f"{file_path} has an unknown file signature.")

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