# ============================================================
# routes/upload.py — File Upload & Flexible Column Mapping
#
# This module handles two steps of the data upload process:
#
# STEP 1 — POST /api/upload/
#   Receives the uploaded CSV or Excel file, saves it, reads
#   the column names, and automatically tries to match them
#   to the system's expected column names using keyword matching.
#   Returns the suggested mapping for the user to confirm.
#
# STEP 2 — POST /api/upload/confirm
#   Receives the user-confirmed column mapping, renames the
#   columns accordingly, cleans the data, and saves a final
#   cleaned CSV that all other modules (analysis, ML) will use.
#
# This flexible approach means the system works even when the
# uploaded file uses different column names like "Item" instead
# of "Product" or "Price" instead of "Unit_Price".
# ============================================================

from flask import Blueprint, request, jsonify
import os
import pandas as pd
import sys

# Add root to path so we can import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS

# Create the upload blueprint
upload_bp = Blueprint('upload', __name__)

# ── Expected System Columns ──────────────────────────────────
# These are the standard column names the system expects.
# Each key is the expected name; the value is a list of
# common alternative names that should map to it.
EXPECTED_COLUMNS = {
    'Customer_Name': ['customer', 'name', 'client', 'buyer',
                      'customer_name', 'customername', 'full_name'],
    'Sex':           ['sex', 'gender', 'male', 'female'],
    'Product':       ['product', 'item', 'goods', 'product_name',
                      'itemname', 'description', 'article'],
    'Category':      ['category', 'type', 'group', 'dept',
                      'department', 'product_type', 'section'],
    'Quantity':      ['quantity', 'qty', 'units', 'amount_sold',
                      'number', 'count', 'pieces'],
    'Date':          ['date', 'transaction_date', 'sale_date',
                      'day', 'time', 'datetime'],
    'Unit_Price':    ['unit_price', 'price', 'cost', 'rate',
                      'unit_cost', 'selling_price', 'unitprice'],
    'Amount':        ['amount', 'total', 'revenue', 'sales',
                      'total_amount', 'total_price', 'totalprice'],
    'Channel':       ['channel', 'platform', 'source',
                      'sales_channel', 'medium', 'mode']
}


def allowed_file(filename):
    """
    Checks if the uploaded file has an allowed extension.
    Returns True for CSV and Excel files, False for everything else.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def auto_map_columns(uploaded_columns):
    """
    Automatically maps uploaded column names to expected column names
    using keyword/fuzzy matching.

    For each uploaded column, we check if its name (lowercased and
    underscored) contains or matches any known keyword for each
    expected column.

    Parameters:
        uploaded_columns (list): Column names from the uploaded file

    Returns:
        mapping (dict): { uploaded_col_name: matched_expected_col or None }
    """
    mapping = {}

    for col in uploaded_columns:
        # Normalize: lowercase and replace spaces with underscores
        lower_col = col.lower().strip().replace(' ', '_')
        matched = None

        for expected_col, keywords in EXPECTED_COLUMNS.items():
            # Check if any keyword matches the uploaded column name
            if any(kw in lower_col or lower_col in kw for kw in keywords):
                matched = expected_col
                break  # Stop at first match

        mapping[col] = matched  # None if no match found

    return mapping


def apply_mapping(df, mapping):
    """
    Renames DataFrame columns based on the confirmed mapping,
    then keeps only columns that have a valid system mapping.

    Parameters:
        df      (DataFrame): Original uploaded data
        mapping (dict)     : { original_col: expected_col }

    Returns:
        DataFrame with renamed and filtered columns
    """
    # Build rename dictionary (skip unmapped columns)
    rename_dict = {k: v for k, v in mapping.items() if v}
    df = df.rename(columns=rename_dict)

    # Keep only columns that exist in the system's expected columns
    keep_cols = [col for col in EXPECTED_COLUMNS.keys() if col in df.columns]
    return df[keep_cols]


def clean_data(df):
    """
    Cleans the DataFrame after column mapping is applied.

    Cleaning steps:
    1. Remove completely empty rows
    2. Standardize text formatting in categorical columns
    3. Normalize Channel values to exactly 'Online' or 'Onsite'
    4. Convert Date column to proper datetime format
    5. Convert numeric columns, replacing invalid values with 0
    6. Remove duplicate rows

    Parameters:
        df (DataFrame): Mapped DataFrame to clean

    Returns:
        Cleaned DataFrame
    """
    # Step 1: Remove rows where ALL columns are empty
    df.dropna(how='all', inplace=True)

    # Step 2: Standardize text columns (strip whitespace, title case)
    for col in ['Product', 'Category', 'Channel', 'Sex', 'Customer_Name']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()

    # Step 3: Normalize Channel to exactly 'Online' or 'Onsite'
    if 'Channel' in df.columns:
        channel_map = {
            'online': 'Online', 'onsite': 'Onsite',
            'Online': 'Online', 'Onsite': 'Onsite',
            'ONLINE': 'Online', 'ONSITE': 'Onsite',
            'In Store': 'Onsite', 'In-Store': 'Onsite',
            'Web': 'Online', 'Internet': 'Online'
        }
        df['Channel'] = df['Channel'].replace(channel_map)

    # Step 4: Convert Date to datetime, drop rows with invalid dates
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df.dropna(subset=['Date'], inplace=True)

    # Step 5: Convert numeric columns, fill invalid entries with 0
    for col in ['Quantity', 'Amount', 'Unit_Price']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Step 6: Remove exact duplicate rows
    df.drop_duplicates(inplace=True)

    return df


@upload_bp.route('/', methods=['POST'])
def upload_file():
    """
    POST /api/upload/
    STEP 1: Receives the uploaded file, saves it, auto-detects
    column mapping, and returns the suggested mapping for
    the user to review and confirm on the frontend.

    Returns JSON with:
    - suggested_mapping: auto-detected column matches
    - uploaded_columns:  original column names in the file
    - missing_columns:   expected columns not yet matched
    - preview:           first 3 rows of raw data
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Use CSV or Excel'}), 400

    try:
        # Save raw uploaded file to uploads folder
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # Load file into pandas DataFrame
        if file.filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)

        # Auto-detect column mapping
        mapping = auto_map_columns(list(df.columns))

        # Find expected columns that were not matched
        mapped_targets  = [v for v in mapping.values() if v]
        missing_columns = [col for col in EXPECTED_COLUMNS.keys()
                           if col not in mapped_targets]

        return jsonify({
            'message':          'File uploaded. Please confirm column mapping.',
            'filename':         file.filename,
            'uploaded_columns': list(df.columns),
            'suggested_mapping': mapping,
            'missing_columns':  missing_columns,
            'preview':          df.head(3).to_dict(orient='records')
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@upload_bp.route('/confirm', methods=['POST'])
def confirm_mapping():
    """
    POST /api/upload/confirm
    STEP 2: Receives the user-confirmed column mapping,
    reloads the original file, applies the mapping,
    cleans the data, and saves the cleaned version.

    Request body:
    {
        "filename": "sales.csv",
        "mapping": { "Item": "Product", "Price": "Unit_Price", ... }
    }

    Returns JSON with:
    - rows:    number of clean records saved
    - columns: final column names
    - preview: first 5 rows of cleaned data
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    filename = data.get('filename')
    mapping  = data.get('mapping', {})

    if not filename:
        return jsonify({'error': 'No filename provided'}), 400

    try:
        # Reload the original uploaded file
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)

        # Apply confirmed column mapping
        df = apply_mapping(df, mapping)

        # Clean the mapped data
        df = clean_data(df)

        # Save final cleaned CSV for use by analysis and ML modules
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