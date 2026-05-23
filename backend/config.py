# ============================================================
# config.py — Application Configuration
# This file defines global settings used across the backend
# such as file paths, allowed file types, and size limits.
# ============================================================

import os

# Base directory of this config file (backend/)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Path where uploaded files will be saved
# Goes one level up from backend/ into data/uploads/
UPLOAD_FOLDER = os.path.join(BASE_DIR, '..', 'data', 'uploads')

# Only these file extensions are accepted for upload
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

# Maximum file size allowed for upload (10 megabytes)
MAX_CONTENT_LENGTH = 10 * 1024 * 1024

# Automatically create the uploads folder if it doesn't exist
# exist_ok=True means no error is raised if folder already exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)