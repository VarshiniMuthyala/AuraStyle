"""
AuraStyle Configuration
Loads environment variables and provides app-wide settings.
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Config:
    # MongoDB
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/aurastyle")
    DB_NAME = os.getenv("DB_NAME", "aurastyle")

    # Flask
    PORT = int(os.getenv("PORT", 5000))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "aurastyle-secret-key-2024")

    # Upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # CLIP model
    CLIP_MODEL = "ViT-B/32"

    # Search
    TOP_K_RESULTS = 20

config = Config()
