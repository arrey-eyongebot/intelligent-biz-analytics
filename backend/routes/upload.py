from flask import Blueprint, request, jsonify
import os
import pandas as pd
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS

upload_bp = Blueprint('upload', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Use CSV or Excel'}), 400

    try:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # Load and clean the data
        if file.filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)

        # Basic cleaning
        df = clean_data(df)

        # Save cleaned version
        cleaned_path = os.path.join(UPLOAD_FOLDER, 'cleaned_data.csv')
        df.to_csv(cleaned_path, index=False)

        return jsonify({
            'message': 'File uploaded and cleaned successfully',
            'rows': len(df),
            'columns': list(df.columns),
            'preview': df.head(5).to_dict(orient='records')
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def clean_data(df):
    # Standardize column names
    df.columns = [col.strip().title().replace(' ', '_') for col in df.columns]

    # Drop fully empty rows
    df.dropna(how='all', inplace=True)

    # Standardize text columns
    for col in ['Product', 'Category', 'Channel', 'Sex']:
        if col in df.columns:
            df[col] = df[col].str.strip().str.title()

    # Standardize Channel values
    if 'Channel' in df.columns:
        df['Channel'] = df['Channel'].replace({
            'Online': 'Online', 'Onsite': 'Onsite',
            'online': 'Online', 'onsite': 'Onsite',
            'ONLINE': 'Online', 'ONSITE': 'Onsite'
        })

    # Convert Date column
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df.dropna(subset=['Date'], inplace=True)

    # Convert numeric columns
    for col in ['Quantity', 'Amount', 'Unit_Price']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col].fillna(0, inplace=True)

    # Remove duplicates
    df.drop_duplicates(inplace=True)

    return df