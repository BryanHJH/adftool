from flask import Flask, render_template
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy

# Application
app = Flask(__name__)

#  Index page
@app.route("/")
def index():
    return render_template("index.html")

if __name__ in "__main__":
    app.run(port=5001, debug=True)