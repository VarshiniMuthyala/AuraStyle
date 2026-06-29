"""
AuraStyle - Upload Route
POST /upload → save an image file and return its server path
"""

import os
import uuid
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
from config import config

upload_bp = Blueprint("upload", __name__)

ALLOWED = config.ALLOWED_EXTENSIONS


def _allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED


@upload_bp.route("/upload", methods=["POST"])
def upload_image():
    """Upload one or more images and return their server-side URLs."""
    if "images" not in request.files and "image" not in request.files:
        return jsonify({"success": False, "error": "No image files provided"}), 400

    # Accept either 'image' (single) or 'images' (multiple)
    files = request.files.getlist("images") or request.files.getlist("image")
    saved = []

    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)

    for file in files:
        if file.filename == "":
            continue
        if not _allowed(file.filename):
            continue
        ext = file.filename.rsplit(".", 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        path = os.path.join(config.UPLOAD_FOLDER, filename)
        file.save(path)
        saved.append({"filename": filename, "url": f"/uploads/{filename}"})

    if not saved:
        return jsonify({"success": False, "error": "No valid images uploaded"}), 400

    return jsonify({"success": True, "files": saved})
