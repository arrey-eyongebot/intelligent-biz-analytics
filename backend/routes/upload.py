# ============================================================
# routes/upload.py — Smart File Upload & Column Mapping
#
# STEP 1 — POST /api/upload/
#   Receives uploaded CSV/Excel, checks if required columns
#   match perfectly. If yes, saves and returns 'perfect_match'.
#   If no, returns the required columns and uploaded columns
#   so the user can manually map them on the frontend.
#
# STEP 2 — POST /api/upload/confirm
#   Receives the user's confirmed mapping, applies it,
#   drops unmatched columns, cleans and saves the data.
# ============================================================

from flask import Blueprint, request, jsonify
import os
import pandas as pd
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS

upload_bp = Blueprint('upload', __name__)

# ── Required columns the system needs to function ────────────
REQUIRED_COLUMNS = [
    'Product', 'Category', 'Quantity',
    'Date', 'Unit_Price', 'Amount', 'Channel'
]

# ── Optional columns kept if present ─────────────────────────
OPTIONAL_COLUMNS = ['Customer_Name', 'Sex']

# All system columns
ALL_COLUMNS = REQUIRED_COLUMNS + OPTIONAL_COLUMNS


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def clean_data(df):
    """
    Cleans the DataFrame after column mapping is applied.
    """
    df.dropna(how='all', inplace=True)

    for col in ['Product', 'Category', 'Channel', 'Sex', 'Customer_Name']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()

    if 'Channel' in df.columns:
        channel_map = {
            'online': 'Online', 'onsite': 'Onsite',
            'Online': 'Online', 'Onsite': 'Onsite',
            'ONLINE': 'Online', 'ONSITE': 'Onsite',
            'In Store': 'Onsite', 'In-Store': 'Onsite',
            'Web': 'Online', 'Internet': 'Online'
        }
        df['Channel'] = df['Channel'].replace(channel_map)

    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df.dropna(subset=['Date'], inplace=True)

    for col in ['Quantity', 'Amount', 'Unit_Price']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    df.drop_duplicates(inplace=True)
    return df


def check_perfect_match(uploaded_columns):
    """
    Checks if all required columns exist exactly in the
    uploaded file columns (case-insensitive check).

    Returns:
        is_perfect (bool): True if all required columns found
        col_map    (dict): Mapping of system col to uploaded col
    """
    # Normalize uploaded columns for comparison
    upper_map = {col.strip().upper(): col for col in uploaded_columns}
    col_map   = {}
    missing   = []

    for req in REQUIRED_COLUMNS:
        if req.upper() in upper_map:
            col_map[req] = upper_map[req.upper()]
        else:
            missing.append(req)

    # Also check optional columns
    for opt in OPTIONAL_COLUMNS:
        if opt.upper() in upper_map:
            col_map[opt] = upper_map[opt.upper()]

    is_perfect = len(missing) == 0
    return is_perfect, col_map, missing


@upload_bp.route('/', methods=['POST'])
def upload_file():
    """
    POST /api/upload/
    Uploads file and checks column match.

    Returns:
    - If perfect match:
      { perfect_match: true, rows, columns, preview }

    - If not perfect match:
      { perfect_match: false,
        required_columns: [...],
        optional_columns: [...],
        uploaded_columns: [...],
        filename: '...' }
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Use CSV or Excel'}), 400

    try:
        # Save the uploaded file
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # Load into DataFrame
        if file.filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)

        uploaded_columns = list(df.columns)

        # Check if columns match perfectly
        is_perfect, col_map, missing = check_perfect_match(uploaded_columns)

        if is_perfect:
            # Rename columns to exact system names
            reverse_map = {v: k for k, v in col_map.items()}
            df = df.rename(columns=reverse_map)

            # Keep only system columns
            keep = [c for c in ALL_COLUMNS if c in df.columns]
            df   = df[keep]

            # Clean and save
            df = clean_data(df)
            cleaned_path = os.path.join(UPLOAD_FOLDER, 'cleaned_data.csv')
            df.to_csv(cleaned_path, index=False)

            return jsonify({
                'perfect_match': True,
                'message':       'All columns matched perfectly!',
                'rows':          len(df),
                'columns':       list(df.columns),
                'preview':       df.head(3).to_dict(orient='records')
            }), 200

        else:
            # Return columns for manual mapping
            return jsonify({
                'perfect_match':    False,
                'message':          'Some columns could not be matched. Please map them manually.',
                'required_columns': REQUIRED_COLUMNS,
                'optional_columns': OPTIONAL_COLUMNS,
                'uploaded_columns': uploaded_columns,
                'missing_columns':  missing,
                'filename':         file.filename
            }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@upload_bp.route('/confirm', methods=['POST'])
def confirm_mapping():
    """
    POST /api/upload/confirm
    Receives user mapping: { system_col: uploaded_col }
    Applies mapping, drops unmatched columns, cleans data.

    Request body:
    {
        "filename": "sales.csv",
        "mapping": {
            "Product":    "Item",
            "Category":   "Type",
            "Quantity":   "Qty",
            "Date":       "Date",
            "Unit_Price": "Price",
            "Amount":     "Total",
            "Channel":    "Store_Type"
        }
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    filename = data.get('filename')
    mapping  = data.get('mapping', {})

    if not filename:
        return jsonify({'error': 'No filename provided'}), 400

    # Check all required columns are mapped
    unmapped = [col for col in REQUIRED_COLUMNS if col not in mapping]
    if unmapped:
        return jsonify({
            'error': f'Please map these required columns: {", ".join(unmapped)}'
        }), 400

    try:
        # Reload original file
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)

        # Build rename dict: uploaded_col → system_col
        # mapping is { system_col: uploaded_col }
        rename_dict = {v: k for k, v in mapping.items() if v}
        df = df.rename(columns=rename_dict)

        # Keep only system columns that exist after renaming
        keep = [c for c in ALL_COLUMNS if c in df.columns]
        df   = df[keep]

        # Clean the data
        df = clean_data(df)

        # Save cleaned data
        cleaned_path = os.path.join(UPLOAD_FOLDER, 'cleaned_data.csv')
        df.to_csv(cleaned_path, index=False)

        return jsonify({
            'message': 'Data mapped and saved successfully!',
            'rows':    len(df),
            'columns': list(df.columns),
            'preview': df.head(5).to_dict(orient='records')
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500