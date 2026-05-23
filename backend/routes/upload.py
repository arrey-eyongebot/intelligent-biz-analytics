# ============================================================
# routes/upload.py — File Upload & Data Cleaning Endpoint
# Handles receiving uploaded CSV/Excel files from the frontend,
# validates them, cleans the data, and saves a cleaned version
# for use by the analysis and prediction modules.
# ============================================================

from flask import Blueprint, request, jsonify
import os
import pandas as pd
import sys

# Add root directory to path so we can import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS

# Create a Blueprint named 'upload'
# Blueprints allow us to organize routes into separate files
upload_bp = Blueprint('upload', __name__)


def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension.
    Returns True if the file is CSV or Excel, False otherwise.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route('/', methods=['POST'])
def upload_file():
    """
    POST /api/upload/
    Accepts a file from the frontend form, validates it,
    saves it, cleans it, and returns a preview of the data.
    """

    # Check if a file was included in the request
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    # Check if a file was actually selected
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Check if the file type is allowed
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Use CSV or Excel'}), 400

    try:
        # Save the raw uploaded file to the uploads folder
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # Load the file into a pandas DataFrame based on its extension
        if file.filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)

        # Clean the data using our cleaning function
        df = clean_data(df)

        # Save the cleaned data as a standard CSV for other modules to use
        cleaned_path = os.path.join(UPLOAD_FOLDER, 'cleaned_data.csv')
        df.to_csv(cleaned_path, index=False)

        # Return success response with basic info about the uploaded data
        return jsonify({
            'message': 'File uploaded and cleaned successfully',
            'rows':    len(df),                          # Number of records
            'columns': list(df.columns),                 # Column names
            'preview': df.head(5).to_dict(orient='records')  # First 5 rows
        }), 200

    except Exception as e:
        # Return error details if anything goes wrong
        return jsonify({'error': str(e)}), 500


def clean_data(df):
    """
    Cleans the uploaded DataFrame by:
    - Standardizing column names
    - Removing empty rows
    - Fixing text formatting
    - Converting date and numeric columns
    - Removing duplicate records
    """

    # Standardize column names: strip spaces, title case, replace spaces with underscores
    # e.g. "product name" becomes "Product_Name"
    df.columns = [col.strip().title().replace(' ', '_') for col in df.columns]

    # Remove rows where ALL columns are empty
    df.dropna(how='all', inplace=True)

    # Standardize text in categorical columns (strip spaces, title case)
    for col in ['Product', 'Category', 'Channel', 'Sex']:
        if col in df.columns:
            df[col] = df[col].str.strip().str.title()

    # Normalize Channel values to exactly 'Online' or 'Onsite'
    # This handles variations like 'online', 'ONLINE', etc.
    if 'Channel' in df.columns:
        df['Channel'] = df['Channel'].replace({
            'Online': 'Online', 'Onsite': 'Onsite',
            'online': 'Online', 'onsite': 'Onsite',
            'ONLINE': 'Online', 'ONSITE': 'Onsite'
        })

    # Convert Date column to proper datetime format
    # errors='coerce' turns unparseable dates into NaT (Not a Time)
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df.dropna(subset=['Date'], inplace=True)  # Remove rows with invalid dates

    # Convert numeric columns, replacing invalid values with 0
    for col in ['Quantity', 'Amount', 'Unit_Price']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col].fillna(0, inplace=True)

    # Remove exact duplicate rows
    df.drop_duplicates(inplace=True)

    return df