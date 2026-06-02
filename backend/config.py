# ============================================================
# config.py — Global Application Configuration
#
# Defines shared settings used across the entire backend:
# - Where uploaded files are stored
# - Which file types are allowed
# - Maximum upload file size
#
# Any module can import from here instead of hardcoding paths.
# ============================================================

import os

# Absolute path of the backend/ directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))


# Path where all uploaded files will be saved
# Resolves to: intelligent-biz-analytics/data/uploads/
if os.environ.get('RENDER'):
    # On Render free plan use /tmp — writable but resets on restart
    UPLOAD_FOLDER = '/tmp/uploads'
else:
    UPLOAD_FOLDER = os.path.join(ROOT_DIR, 'data', 'uploads')
# Only these file extensions are accepted during upload
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

# Maximum allowed upload size: 10 megabytes
# 1024 bytes = 1 KB, 1024 KB = 1 MB, so 10 * 1024 * 1024 = 10 MB
MAX_CONTENT_LENGTH = 10 * 1024 * 1024

# Automatically create the uploads folder if it does not exist
# exist_ok=True prevents an error if the folder already exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)