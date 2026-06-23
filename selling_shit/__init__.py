from pathlib import Path

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_UPLOAD_DIR = BASE_DIR / "uploads"

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = str(DEFAULT_UPLOAD_DIR)


@app.route("/", methods=["GET", "POST"])
def home():
    draft = None

    if request.method == "POST":
        upload_dir = Path(app.config["UPLOAD_FOLDER"])
        upload_dir.mkdir(parents=True, exist_ok=True)
        saved_files = []

        for uploaded_file in request.files.getlist("images"):
            if not uploaded_file or not uploaded_file.filename:
                continue

            filename = secure_filename(uploaded_file.filename)
            if not filename:
                continue

            uploaded_file.save(upload_dir / filename)
            saved_files.append(filename)

        draft = {
            "title": request.form.get("title", "").strip(),
            "description": request.form.get("description", "").strip(),
            "price": request.form.get("price", "").strip(),
            "saved_files": saved_files,
        }

    return render_template("home.html", draft=draft)
