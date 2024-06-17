import os
import sys
import subprocess
import zipfile

from flask import Flask, render_template, request, send_from_directory, send_file
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from io import BytesIO
from datetime import datetime

sys.path.insert(1, os.path.join(os.path.dirname(__file__), './scripts'))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), './bin'))
from magic_byte_analysis import analyze_file as magic_byte_analysis
from image_analyze import analyze_file as steganalysis
from pcap_analyze import analyze_pcap as pcapanalysis

# Application
app = Flask(__name__)

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# Directory to store all relevant files
UPLOAD_FOLDER = "/home/data"
RESULT_FOLDER = "/home/results"
BIN_FOLDER = "/home/bin"
SCRIPTS_FOLDER = "/home/scripts"

class Scans(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(50), nullable=False)
    resultpath = db.Column(db.String(), nullable=False) # Storing the file path instead of the file itself
    fileextension = db.Column(db.String(50))
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Scan %r>' % self.id
    
def get_result_files(result_path):
    result_files = []
    file_contents = {}
    images = []

    for root, dirs, files in os.walk(result_path):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, result_path)
            result_files.append(relative_path)

            if file.endswith('.txt') or file.endswith('.bin'):
                with open(file_path, 'rb') as f:
                    content = f.read().decode('utf-8', 'ignore')
                    if content.strip():
                        file_contents[relative_path] = content

            elif file.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                images.append(relative_path)

    return result_files, file_contents, images

#  Index page
@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        file = request.files["file"]
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename) # The path to the file
        result_path = os.path.join(RESULT_FOLDER, f"results_{os.path.basename(file_path)}") # The path to the result

        progress_messages = ""
        
        try:
            file.save(file_path)
        except Exception as e:
            upload_message = f"Error: {e}"
            return f"Error: {upload_message}"

        try:
            # Check if the file exists in the /home/data/ directory
            if os.path.exists(file_path):
                # Perform magic byte analysis and file signature checks using analyze_file
                is_match, signature_message, magic_bytes_message, file_extension, has_extension = magic_byte_analysis(file_path, verbose=False)

                if has_extension:
                    if is_match and file_extension.lower() in ["png", "jpg", "jpeg", "gif", "bmp"]:
                        os.makedirs(result_path, exist_ok=True)
                        try:
                            # Performing steganalysis if the uploaded file is an image file and passes the magic bytes analysis check
                            subprocesses, progress_messages = steganalysis(file_path, verbose=False)
                            # return render_template("index.html", scans=Scans.query.order_by(Scans.date).all(), signature_message=signature_message, magic_bytes_message=magic_bytes_message, progress_messages=progress_messages)
                        except subprocess.CalledProcessError as e:
                            error_message = f"Error executing steganalysis script: {str(e)}\nReturn code: {e.returncode}\nOutput: {e.output}"
                            return error_message
                        except Exception as e:
                            error_message = f"Error during steganalysis: {str(e)}"
                            return error_message
                        
                    elif is_match and file_extension.lower() in ["pcap", "pcapng"]:
                        try:
                            # Performing pcap analysis using tshark if the uploaded file is a PCAP or PCAPNG file and passes the magic bytes analysis check
                            subprocesses, progress_messages = pcapanalysis(file_path, verbose=False)
                            # return render_template("index.html", scans=Scans.query.order_by(Scans.date).all(), signature_message=signature_message, magic_bytes_message=magic_bytes_message)
                        except subprocess.CalledProcessError as e:
                            error_message = f"Error executing PCAP analysis script: {str(e)}\nReturn code: {e.returncode}\nOutput: {e.output}"
                            return error_message
                        except Exception as e:
                            error_message = f"Error during PCAP analysis: {str(e)}"
                            return error_message
                
                scan = Scans(filename=filename, resultpath=result_path, fileextension=file_extension)

                try:
                    db.session.add(scan)
                    db.session.commit()
                    return render_template("index.html", scans=Scans.query.order_by(Scans.date).all(), signature_message=signature_message, magic_bytes_message=magic_bytes_message, progress_messages=progress_messages)
                except Exception as e:
                    db.session.rollback()
                    return f"Error adding scan to the database: {str(e)}. There was an issue adding your scan"
            else:
                raise FileNotFoundError(f"File not found: {file_path}")
        except FileNotFoundError as e:
            return f"Error: str(e).\nThe uploaded file was not found."
        except Exception as e:
            return f"Error analyzing file: {str(e)}.\nThere was an issue analyzing the file.\n{list(filter(os.path.isfile, os.listdir('/home/data')))}"


    else:
        return render_template("index.html", scans=Scans.query.order_by(Scans.date).all())
    
# Viewing the record
@app.route("/view/<int:id>")
def view(id):
    scan = Scans.query.get_or_404(id)
    result_files, file_contents, images = get_result_files(scan.resultpath)
    result_files.sort()
    return render_template("view.html", scan=scan, result_files=result_files, file_contents=file_contents, images=images)

@app.route("/download_result/<int:scan_id>/<path:filename>")
def download_result(scan_id, filename):
    scan = Scans.query.get_or_404(scan_id)
    return send_from_directory(scan.resultpath, filename, as_attachment=True)

@app.route("/download_all/<int:scan_id>", methods=["POST"])
def download_all_results(scan_id):
    scan = Scans.query.get_or_404(scan_id)
    result_files, _, _ = get_result_files(scan.resultpath)

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for file in result_files:
            file_path = os.path.join(scan.resultpath, file)
            zip_file.write(file_path, file)

    zip_buffer.seek(0)
    return send_file(zip_buffer, as_attachment=True, download_name=f"{scan.filename}_results.zip")

@app.route("/image/<int:scan_id>/<path:filename>")
def get_image(scan_id, filename):
    scan = Scans.query.get_or_404(scan_id)
    image_path = os.path.join(scan.resultpath, filename)
    return send_file(image_path)

if __name__ in "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()
    app.run(host='0.0.0.0', port=5001, debug=True)