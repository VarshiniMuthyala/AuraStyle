"""
AuraStyle - Main Flask Application
Multimodal AI Fashion Discovery Platform
"""

import os
from flask import Flask, send_from_directory, render_template
from flask_cors import CORS

from config import config
from database.routes import products_bp, search_bp, upload_bp


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    # ── Configuration ───────────────────────────────────────────────────────
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH
    app.config["UPLOAD_FOLDER"] = config.UPLOAD_FOLDER

    # ── CORS (allow all origins for dev) ────────────────────────────────────
    CORS(app, resources={r"/*": {"origins": "*"}})

    # ── Blueprints ──────────────────────────────────────────────────────────
    app.register_blueprint(products_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(upload_bp)

    # ── Serve uploaded files ─────────────────────────────────────────────────
    @app.route("/uploads/<path:filename>")
    def serve_upload(filename):
        return send_from_directory(config.UPLOAD_FOLDER, filename)

    # ── Frontend ─────────────────────────────────────────────────────────────
    @app.route("/")
    def index():
        return render_template("index.html")

    # ── Health check ─────────────────────────────────────────────────────────
    @app.route("/health")
    def health():
        return {"status": "ok", "service": "AuraStyle AI Fashion API"}

    # ── Ensure upload folder exists ──────────────────────────────────────────
    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(
        host="0.0.0.0",
        port=config.PORT,
        debug=config.DEBUG,
    )
