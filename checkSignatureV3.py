# import os
# import json
# import filetype

# def check_file_signature(file_path, ext):
#     kind = None
#     with open(file_path, 'rb') as file:
#         kind = filetype.match(file.read(32))
#     if kind is None:
#         return f"Cannot guess file type for {file_path}, file might be corrupted"
#     correct_ext = kind.extension
#     if os.path.splitext(file_path)[1] == '':
#         return f"File extension should be {correct_ext}"
#     elif correct_ext == ext or ext == '':
#         return f"File extension {correct_ext} and file signature matches"
#     else:
#         return f"The current file extension is {ext}, and it should be {correct_ext}, what the current file's signature is {kind.mime}"

# def scan_directory(dir_path, ext):
#     results = {}
#     for root, dirs, files in os.walk(dir_path):
#         for file in files:
#             file_path = os.path.join(root, file)
#             if file.endswith(ext) or ext == '' or os.path.splitext(file_path)[1] == '':
#                 results[file_path] = check_file_signature(file_path, ext)
#     with open('results.json', 'w') as file:
#         json.dump(results, file)

# def main():
#     path = input("Enter the file or directory path: ")
#     ext = input("Enter the file extension (leave blank to check all files): ")
#     if os.path.isfile(path):
#         print(check_file_signature(path, ext))
#     elif os.path.isdir(path):
#         scan_directory(path, ext)
#     else:
#         print("Invalid path")

# if __name__ == "__main__":
#     main()


import os
import json
import binascii

# Dictionary of file signatures
SIGNATURES = {
    'jpg': b'\xFF\xD8\xFF',
    'png': b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A',
    'gif': b'\x47\x49\x46\x38',
    # Add more signatures as needed
}

def get_file_signature(file_path, max_bytes=32):
    with open(file_path, 'rb') as f:
        header = f.read(max_bytes)
    return header

def check_file_signature(file_path, extension):
    file_ext = os.path.splitext(file_path)[1][1:].lower()
    if file_ext:
        if file_ext != extension.lower():
            return f"Skipping {file_path} as it does not have the '{extension}' extension."
    else:
        header = get_file_signature(file_path)
        for ext, sig in SIGNATURES.items():
            if header.startswith(sig):
                return f"File extension should be {ext}. Current header: {binascii.hexlify(header).decode()}, Expected header: {binascii.hexlify(sig).decode()}"
        return f"Cannot guess file type for {file_path}, file might be corrupted"