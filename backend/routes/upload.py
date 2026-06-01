# ============================================================
# routes/upload.py — Smart File Upload & Column Mapping
#
# STEP 1 — POST /api/upload/
#   Checks if uploaded file columns match the system perfectly.
#   If yes → cleans and saves data, returns perfect_match=True.
#   If no  → returns columns for manual mapping on frontend.
#
# STEP 2 — POST /api/upload/confirm
#   Applies the user's confirmed mapping.
#   Handles three smart defaults for unmapped columns:
#     - Amount   → calculated as Quantity × Unit_Price
#     - Channel  → filled with 'Onsite'
#     - Category → filled with 'Consumables'
#   All other unmapped columns are dropped.
# ============================================================

from flask import Blueprint, request, jsonify
import os
import pandas as pd
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS

upload_bp = Blueprint('upload', __name__)

# ── Required system columns ───────────────────────────────────
REQUIRED_COLUMNS = [
    'Product', 'Category', 'Quantity',
    'Date', 'Unit_Price', 'Amount', 'Channel'
]

# ── Optional system columns ───────────────────────────────────
OPTIONAL_COLUMNS = ['Customer_Name', 'Sex']

# ── All system columns ────────────────────────────────────────
ALL_COLUMNS = REQUIRED_COLUMNS + OPTIONAL_COLUMNS

# ── Default values for columns that can be auto-filled ───────
# These columns do not need to be mapped by the user.
# If unmapped, they are filled with these defaults.
COLUMN_DEFAULTS = {
    'Channel':  'Onsite',       # All sales default to Onsite
    'Category': 'Consumables',  # All products default to Consumables
    # Amount is handled separately (Quantity × Unit_Price)
}


def allowed_file(filename):
    """Check if file extension is allowed (CSV or Excel)."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def clean_data(df):
    """
    Cleans the DataFrame after column mapping is applied.
    Steps:
    1. Remove empty rows
    2. Standardize text columns
    3. Normalize Channel values
    4. Convert Date to datetime
    5. Convert numeric columns
    6. Remove duplicates
    """
    # Remove completely empty rows
    df.dropna(how='all', inplace=True)

    # Standardize text columns
    for col in ['Product', 'Category', 'Channel', 'Sex', 'Customer_Name']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()

    # Normalize Channel to exactly Online or Onsite
    if 'Channel' in df.columns:
        channel_map = {
            'Online': 'Online',   'Onsite': 'Onsite',
            'online': 'Online',   'onsite': 'Onsite',
            'ONLINE': 'Online',   'ONSITE': 'Onsite',
            'In Store': 'Onsite', 'In-Store': 'Onsite',
            'Web': 'Online',      'Internet': 'Online'
        }
        df['Channel'] = df['Channel'].replace(channel_map)

    # Convert Date column to datetime format
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df.dropna(subset=['Date'], inplace=True)

    # Convert numeric columns, fill invalid with 0
    for col in ['Quantity', 'Amount', 'Unit_Price']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Remove duplicate rows
    df.drop_duplicates(inplace=True)

    return df


def check_perfect_match(uploaded_columns):
    """
    Checks if all required columns exist in the uploaded file
    using case-insensitive matching.

    Returns:
        is_perfect (bool): True if all required columns found
        col_map    (dict): { system_col: uploaded_col }
        missing    (list): Required columns not found
    """
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
    Receives uploaded file and checks column match.

    Returns:
    - Perfect match:
      { perfect_match: true, rows, columns, preview }
    - Mismatch:
      { perfect_match: false, required_columns,
        optional_columns, uploaded_columns,
        missing_columns, filename }
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

        # Check if all columns match perfectly
        is_perfect, col_map, missing = check_perfect_match(uploaded_columns)

        if is_perfect:
            # Rename to exact system column names
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
                'message':          'Some columns could not be matched.',
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
    Applies user-confirmed column mapping with smart defaults.

    Smart defaults for unmapped columns:
    - Amount   → calculated as Quantity × Unit_Price
    - Channel  → all rows filled with 'Onsite'
    - Category → all rows filled with 'Consumables'

    Request body:
    {
        "filename": "sales.csv",
        "mapping": {
            "Product":    "Item",
            "Quantity":   "Qty",
            "Date":       "Date",
            "Unit_Price": "Price"
            // Amount, Channel, Category can be omitted
            // they will use defaults
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

    # Check that truly required columns (no defaults) are mapped
    must_map = [col for col in REQUIRED_COLUMNS
                if col not in COLUMN_DEFAULTS and col != 'Amount']
    unmapped = [col for col in must_map if col not in mapping]

    if unmapped:
        return jsonify({
            'error': f'Please map these required columns: '
                     f'{", ".join(unmapped)}'
        }), 400

    try:
        # Reload the original uploaded file
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

        # ── Apply Smart Defaults ──────────────────────────────

        # Default 1: Channel → 'Onsite' if not mapped
        if 'Channel' not in df.columns:
            df['Channel'] = 'Onsite'

        # Default 2: Category → 'Consumables' if not mapped
        if 'Category' not in df.columns:
            df['Category'] = 'Consumables'

        # Default 3: Amount → Quantity × Unit_Price if not mapped
        if 'Amount' not in df.columns:
            if 'Quantity' in df.columns and 'Unit_Price' in df.columns:
                # Convert to numeric first to avoid string multiplication
                df['Quantity']   = pd.to_numeric(
                    df['Quantity'],   errors='coerce').fillna(0)
                df['Unit_Price'] = pd.to_numeric(
                    df['Unit_Price'], errors='coerce').fillna(0)
                df['Amount'] = df['Quantity'] * df['Unit_Price']
            else:
                df['Amount'] = 0  # Fallback if both are missing

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
