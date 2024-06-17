import subprocess
import os

def execute_script(script_path, file_path, result_dir, verbose):
    try:
        process = subprocess.Popen([script_path, file_path, result_dir, "-v" if verbose else ""],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        return process, f"{os.path.basename(script_path)} analysis started."
    except subprocess.CalledProcessError as e:
        error_message = f"Error executing {os.path.basename(script_path)} script: {str(e)}\nReturn code: {e.returncode}\nOutput: {e.output}"
        raise Exception(error_message)