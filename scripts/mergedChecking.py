import os
import subprocess
import filetype
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

def compare_magic_bytes(file_path, guessed_extension):
    file_obj = FileObject(file_path)
    header = file_obj.fileStream.read(32)
    
    for sig_dict in file_obj.allFileTypes:
        size, offset, magic_hex, ext, desc = sig_dict.strip().split('|')
        if ext == guessed_extension:
            size = int(size)
            offset = int(offset)
            file_obj.fileStream.seek(offset)
            file_magic_bytes = file_obj.fileStream.read(size).hex().upper()
            expected_magic_bytes = magic_hex
            
            if file_magic_bytes == expected_magic_bytes:
                return True, None
            else:
                return False, (file_magic_bytes, expected_magic_bytes)
    
    return False, None

def analyze_file(file_path, verbose):
    is_match, sig_dict = check_file_signature(file_path)
    
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
            
            if os.path.exists(result_dir):
                shutil.rmtree(result_dir)
            
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