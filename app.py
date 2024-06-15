import uuid
import os
import sys
import subprocess

from flask import Flask, render_template, request, redirect
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from io import BytesIO
from datetime import datetime

sys.path.insert(1, os.path.join(os.path.dirname(__file__), './scripts'))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), './bin'))
from magic_byte_analysis import analyze_file as magic_byte_analysis
from image_analyze import analyze_file as steganalysis

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
    
def run_shell_scripts(file_path, result_dir, verbose=True):
    scripts = [
        os.path.join(SCRIPTS_FOLDER, "binwalk_analysis.sh"),
        os.path.join(SCRIPTS_FOLDER, "outguess_analysis.sh"),
        os.path.join(SCRIPTS_FOLDER, "stegoveritas_analysis.sh"),
        os.path.join(SCRIPTS_FOLDER, "zsteg_analysis.sh")
    ]

    for script in scripts:
        subprocess.run([script, file_path, result_dir, str(verbose)], check=True)

#  Index page
@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        file = request.files["file"]
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename) # The path to the file
        result_path = os.path.join(RESULT_FOLDER, f"results_{os.path.basename(file_path)}") # The path to the result
        
        try:
            file.save(file_path)
        except Exception as e:
            upload_message = f"Error: {e}"
            return f"Error: {upload_message}"

        # Perform magic byte analysis and file signature checks using analyze_file
        try:
            # Check if the file exists in the /home/data/ directory
            if os.path.exists(file_path):
                # Perform magic byte analysis and file signature checks using analyze_file
                is_match, signature_message, magic_bytes_message, file_extension = magic_byte_analysis(file_path, verbose=False)

                if is_match and file_extension.lower() in ["png", "jpg", "jpeg", "gif", "bmp"]:
                    # result_path = os.path.join(RESULT_FOLDER, f"results_{os.path.basename(file_path)}")
                    os.makedirs(result_path, exist_ok=True)
                    try:
                        subprocesses, progress_messages = steganalysis(file_path, verbose=False)
                        # return render_template("index.html", scans=Scans.query.order_by(Scans.date).all(), signature_message=signature_message, magic_bytes_message=magic_bytes_message, progress_messages=progress_messages)
                    except subprocess.CalledProcessError as e:
                        error_message = f"Error executing steganalysis script: {str(e)}\nReturn code: {e.returncode}\nOutput: {e.output}"
                        return error_message
                    except Exception as e:
                        error_message = f"Error during steganalysis: {str(e)}"
                        return error_message
            else:
                raise FileNotFoundError(f"File not found: {file_path}")
        except FileNotFoundError as e:
            return f"Error: str(e).\nThe uploaded file was not found."
        except Exception as e:
            return f"Error analyzing file: {str(e)}.\nThere was an issue analyzing the file.\n{list(filter(os.path.isfile, os.listdir('/home/data')))}"

        scan = Scans(filename=filename, resultpath=result_path, fileextension=file_extension)

        try:
            db.session.add(scan)
            db.session.commit()
            return render_template("index.html", scans=Scans.query.order_by(Scans.date).all(), signature_message=signature_message, magic_bytes_message=magic_bytes_message, progress_messages=progress_messages)
        except Exception as e:
            db.session.rollback()
            return f"Error adding scan to the database: {str(e)}. There was an issue adding your scan"

    else:
        return render_template("index.html", scans=Scans.query.order_by(Scans.date).all())
# Viewing the record
@app.route("/view/<int:id>")
def view(id):
    scan = Scans.query.get_or_404(id)
    return render_template("view.html", scan=scan)

# Deleting a record (for the dummy data)
@app.route("/delete/<int:id>")
def delete(id):
    scan_to_delete = Scans.query.get_or_404(id)

    try:
        db.session.delete(scan_to_delete)
        db.session.commit()
        return redirect("/")
    except:
        return "There was a problem deleting the scan"

if __name__ in "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()
    app.run(host='0.0.0.0', port=5001, debug=True)