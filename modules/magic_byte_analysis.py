import os
import filetype
import argparse
import sys

# Required to be able to import files from other folders
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '../src'))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '../utils'))
from pyMagicBytes import FileObject
from input_processor import process_input


def write_results(file_path, signature_message, magic_bytes_message):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    result_dir = os.path.join(os.path.dirname(script_dir), "results", f"results_{os.path.basename(file_path)}")
    os.makedirs(result_dir, exist_ok=True)
    with open(os.path.join(result_dir, "MAGIC_BYTES_ANALYSIS.txt"), "w") as f:
        f.write(signature_message + "\n")
        f.write(magic_bytes_message + "\n")

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
    
    return None, None

def analyze_file(file_path, verbose):
    is_match, sig_dict = check_file_signature(file_path)
    current_extension = os.path.splitext(file_path)[1][1:].lower()
    has_extension = bool(current_extension)
    
    if is_match:
        if current_extension:
            is_match, diff = compare_magic_bytes(file_path, current_extension)
            if is_match:
                signature_message = f"{file_path} is a {sig_dict['description']} file with the correct extension."
                file_extension = current_extension
            else:
                signature_message = f"{file_path} has a file extension that does not match its file signature."
                file_extension = None
        else:
            guessed_type = filetype.guess(file_path)
            if guessed_type is None:
                signature_message = f"{file_path} is a {sig_dict['description']} file."
                file_extension = sig_dict.get('file_extension')
            else:
                signature_message = f"{file_path} has no file extension. Expected file type: {sig_dict['description']}"
                signature_message += f"\nRename the file to include the .{guessed_type.extension} extension."
                file_extension = guessed_type.extension
                write_results(file_path, signature_message, "")
    else:
        signature_message = f"{file_path} has an unknown file type."
        file_extension = None
        if not current_extension:
            guessed_type = filetype.guess(file_path)
            if guessed_type is not None:
                signature_message += f"\nGuessed file type: {guessed_type.extension}"
                signature_message += f"\nRename the file to include the .{guessed_type.extension} extension."
    
    if current_extension:
        is_match, diff = compare_magic_bytes(file_path, current_extension)
        
        if is_match:
            magic_bytes_message = f"The magic bytes of {file_path} match the expected magic bytes for {current_extension} files."
        else:
            if diff is not None:
                magic_bytes_message = f"The magic bytes of {file_path} do not match the expected magic bytes for {current_extension} files."
                magic_bytes_message += f"\nFile's magic bytes: {diff[0]}"
                magic_bytes_message += f"\nExpected magic bytes: {diff[1]}"
            else:
                magic_bytes_message = f"No magic byte information found for {current_extension} files."
        
        write_results(file_path, signature_message, magic_bytes_message)
    else:
        magic_bytes_message = f"{file_path} has no file extension."
        guessed_type = filetype.guess(file_path)
        if guessed_type is not None:
            magic_bytes_message += f"\nGuessed file type: {guessed_type.extension}"
            magic_bytes_message += f"\nRename the file to include the .{guessed_type.extension} extension."
    
    if verbose:
        print(signature_message)
        print(magic_bytes_message)
        print(sig_dict["file_extension"])
    
    return is_match, signature_message, magic_bytes_message, file_extension, has_extension

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze files for file signature, magic bytes, and file type guessing.')
    parser.add_argument('input_path', help='File or directory path')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    process_input(args.input_path, analyze_file, args.verbose)