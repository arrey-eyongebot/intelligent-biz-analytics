# ============================================================
# routes/upload.py — Flexible File Upload & Column Mapping
# Handles CSV/Excel uploads with different column names.
# Auto-detects columns using fuzzy matching and allows the
# frontend to confirm or correct the mapping before saving.
# ============================================================

from flask import Blueprint, request, jsonify
import os
import pandas as pd
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS

upload_bp = Blueprint('upload', __name__)

# ── Expected Columns ─────────────────────────────────────────
# These are the standard column names the system needs.
# The mapper will try to match uploaded columns to these.
EXPECTED_COLUMNS = {
    'Customer_Name': ['customer', 'name', 'client', 'buyer', 'customer_name', 'customername'],
    'Sex':           ['sex', 'gender', 'male', 'female'],
    'Product':       ['product', 'item', 'goods', 'product_name', 'itemname', 'description'],
    'Category':      ['category', 'type', 'group', 'dept', 'department', 'product_type'],
    'Quantity':      ['quantity', 'qty', 'units', 'amount_sold', 'number', 'count'],
    'Date':          ['date', 'transaction_date', 'sale_date', 'day', 'time'],
    'Unit_Price':    ['unit_price', 'price', 'cost', 'rate', 'unit_cost', 'selling_price'],
    'Amount':        ['amount', 'total', 'revenue', 'sales', 'total_amount', 'total_price'],
    'Channel':       ['channel', 'platform', 'source', 'sales_channel', 'medium']
}


def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def auto_map_columns(uploaded_columns):
    """
    Automatically maps uploaded column names to expected column names
    using fuzzy/keyword matching.

    For each expected column, checks if any uploaded column name
    contains a known keyword for that column.

    Returns:
        mapping (dict): { uploaded_col: expected_col or None }
    """
    mapping = {}
    uploaded_lower = {col: col.lower().replace(' ', '_')
                      for col in uploaded_columns}

    for uploaded_col, lower_col in uploaded_lower.items():
        matched = None
        for expected_col, keywords in EXPECTED_COLUMNS.items():
            # Check if any keyword matches the uploaded column name
            if any(kw in lower_col or lower_col in kw
                   for kw in keywords):
                matched = expected_col
                break
        mapping[uploaded_col] = matched

    return mapping


def apply_mapping(df, mapping):
    """
    Renames DataFrame columns based on the confirmed mapping.
    Only keeps columns that have a valid mapping.

    Parameters:
        df      : Original DataFrame
        mapping : { original_col: expected_col }
    Returns:
        Renamed and filtered DataFrame
    """
    # Build rename dict (only mapped columns)
    rename_dict = {k: v for k, v in mapping.items() if v}
    df = df.rename(columns=rename_dict)

    # Keep only the expected columns that exist
    keep_cols = [col for col in EXPECTED_COLUMNS.keys()
                 if col in df.columns]
    return df[keep_cols]


def clean_data(df):
    """
    Cleans the DataFrame after column mapping is applied.
    Handles formatting, type conversion and deduplication.
    """
    # Remove fully empty rows
    df.dropna(how='all', inplace=True)

    # Standardize text columns
    for col in ['Product', 'Category', 'Channel', 'Sex', 'Customer_Name']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()

    # Normalize Channel values
    if 'Channel' in df.columns:
        df['Channel'] = df['Channel'].replace({
            'Online': 'Online', 'Onsite': 'Onsite',
            'online': 'Online', 'onsite': 'Onsite',
            'ONLINE': 'Online', 'ONSITE': 'Onsite'
        })

    # Convert Date to datetime
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df.dropna(subset=['Date'], inplace=True)

    # Convert numeric columns
    for col in ['Quantity', 'Amount', 'Unit_Price']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Remove duplicates
    df.drop_duplicates(inplace=True)

    return df


@upload_bp.route('/', methods=['POST'])
def upload_file():
    """
    POST /api/upload/
    Step 1: Upload file and get suggested column mapping.
    Returns the mapping for user confirmation before saving.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Use CSV or Excel'}), 400

    try:
        # Save raw uploaded file
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # Load into DataFrame
        if file.filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)

        # Auto-detect column mapping
        mapping = auto_map_columns(list(df.columns))

        # Check which expected columns are missing
        mapped_targets  = [v for v in mapping.values() if v]
        missing_columns = [col for col in EXPECTED_COLUMNS.keys()
                          if col not in mapped_targets]

        return jsonify({
            'message':         'File uploaded. Please confirm column mapping.',
            'filename':        file.filename,
            'uploaded_columns': list(df.columns),
            'suggested_mapping': mapping,
            'missing_columns': missing_columns,
            'preview':         df.head(3).to_dict(orient='records')
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@upload_bp.route('/confirm', methods=['POST'])
def confirm_mapping():
    """
    POST /api/upload/confirm
    Step 2: Apply the user-confirmed column mapping,
    clean the data, and save it for analysis.

    Request body:
    {
        "filename": "sales.csv",
        "mapping": { "Item": "Product", "Price": "Unit_Price", ... }
    }
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

        # Apply the confirmed mapping
        df = apply_mapping(df, mapping)

        # Clean the mapped data
        df = clean_data(df)

        # Save cleaned data for analysis and ML
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