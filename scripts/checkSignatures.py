import os
import json
import binascii

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

def check_file_signature(file_path, extension):
    file_ext = os.path.splitext(file_path)[1][1:].lower()
    if file_ext:
        if file_ext != extension.lower():
            return f"Skipping {file_path} as it does not have the '{extension}' extension."

        header = get_file_signature(file_path)
        for sig_dict in SIGNATURES:
            if sig_dict['file_extension'] == file_ext:
                sig_bytes = bytes([b for b in sig_dict['hex'] if b is not None])
                if header.startswith(sig_bytes):
                    return f"File extension and file signature matches for {file_path}"
        return f"File signature does not match the expected signature for extension {file_ext}"
    else:
        header = get_file_signature(file_path)
        closest_sig = find_closest_signature(header)
        if closest_sig:
            diff = ''.join(f'{a:02X}' if a == b else f'({a:02X}-{b:02X})' for a, b in zip(header, bytes([b for b in closest_sig['hex'] if b is not None])))
            return f"File extension should be {closest_sig['file_extension']}. Current header: {binascii.hexlify(header).decode()}, Expected header: {diff}"
        else:
            return f"Cannot guess file type for {file_path}, file might be corrupted"

def process_input(input_path, extension, depth=2):
    results = []
    if os.path.isfile(input_path):
        result = check_file_signature(input_path, extension)
        results.append(result)
    elif os.path.isdir(input_path):
        for root, dirs, files in os.walk(input_path):
            for file in files:
                file_path = os.path.join(root, file)
                result = check_file_signature(file_path, extension)
                results.append(result)
            if depth == 0:
                dirs[:] = []
            else:
                dirs[:] = [d for d in dirs if os.path.join(root, d) != input_path]
                depth -= 1
    else:
        print(f"Invalid input: {input_path}")

    if results:
        output_file = "results.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=4)
        print(f"Results saved to {output_file}")

if __name__ == "__main__":
    input_path = input("Enter the file or directory path: ")
    extension = input("Enter the file extension to check (leave blank to check all files): ")
    process_input(input_path, extension)