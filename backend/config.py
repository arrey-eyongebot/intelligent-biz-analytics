import os

# Base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Upload folder
UPLOAD_FOLDER = os.path.join(BASE_DIR, '..', 'data', 'uploads')

# Allowed file extensions
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

# Max file size (10MB)
MAX_CONTENT_LENGTH = 10 * 1024 * 1024

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)