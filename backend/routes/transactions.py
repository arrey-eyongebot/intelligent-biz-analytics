# ============================================================
# routes/transactions.py — Manual Transaction Recording
#
# Allows business owners to record individual sales
# transactions directly through the web app without
# needing to upload a spreadsheet.
#
# Each recorded transaction is:
# 1. Saved to manual_transactions.csv (persistent record)
# 2. Merged into cleaned_data.csv (so analysis includes it)
#
# Endpoints:
#   POST   /api/transactions/add          — Add new transaction
#   GET    /api/transactions/all          — Get all transactions
#   DELETE /api/transactions/delete/<id> — Delete a transaction
# ============================================================

from flask import Blueprint, request, jsonify
import pandas as pd
import os
from datetime import datetime
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.config import UPLOAD_FOLDER

# Create the transactions blueprint
transactions_bp = Blueprint('transactions', __name__)

# Path to the file storing manually recorded transactions
TRANSACTIONS_FILE = os.path.join(UPLOAD_FOLDER, 'manual_transactions.csv')

# Fields that must be provided to record a transaction
REQUIRED_FIELDS = ['Product', 'Category', 'Quantity', 'Unit_Price', 'Channel']


def load_transactions():
    """
    Loads manually recorded transactions from CSV.
    Returns an empty DataFrame with correct columns if
    no transactions have been recorded yet.
    """
    if os.path.exists(TRANSACTIONS_FILE):
        return pd.read_csv(TRANSACTIONS_FILE)

    # Return empty DataFrame with the correct column structure
    return pd.DataFrame(columns=[
        'Customer_Name', 'Sex', 'Product', 'Category',
        'Quantity', 'Date', 'Unit_Price', 'Amount', 'Channel'
    ])


def merge_with_cleaned(new_df):
    """
    Merges newly recorded transactions into the main
    cleaned_data.csv so that the dashboard and analysis
    endpoints automatically include manually entered data.

    Parameters:
        new_df (DataFrame): The new transaction(s) to merge in
    """
    cleaned_path = os.path.join(UPLOAD_FOLDER, 'cleaned_data.csv')
    if os.path.exists(cleaned_path):
        existing = pd.read_csv(cleaned_path)
        merged   = pd.concat([existing, new_df], ignore_index=True)
        merged.drop_duplicates(inplace=True)
        merged.to_csv(cleaned_path, index=False)
    else:
        # If no cleaned data exists yet, create it from transactions
        new_df.to_csv(cleaned_path, index=False)


@transactions_bp.route('/add', methods=['POST'])
def add_transaction():
    """
    POST /api/transactions/add
    Records a single new sales transaction.
    Amount is automatically calculated as Quantity × Unit_Price.

    Required fields:
        Product, Category, Quantity, Unit_Price, Channel

    Optional fields:
        Customer_Name, Sex, Date (defaults to today if omitted)

    Returns the saved transaction and total record count.
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Validate required fields are present and non-empty
    for field in REQUIRED_FIELDS:
        if field not in data or not str(data[field]).strip():
            return jsonify({'error': f'Missing required field: {field}'}), 400

    try:
        quantity   = float(data['Quantity'])
        unit_price = float(data['Unit_Price'])
        amount     = quantity * unit_price  # Auto-calculate total

        # Build the full transaction record
        transaction = {
            'Customer_Name': data.get('Customer_Name', 'Anonymous'),
            'Sex':           data.get('Sex', 'Unknown'),
            'Product':       str(data['Product']).strip().title(),
            'Category':      str(data['Category']).strip().title(),
            'Quantity':      quantity,
            'Date':          data.get('Date',
                             datetime.now().strftime('%Y-%m-%d')),
            'Unit_Price':    unit_price,
            'Amount':        amount,
            'Channel':       str(data['Channel']).strip().title()
        }

        # Load existing transactions and append the new one
        df      = load_transactions()
        new_row = pd.DataFrame([transaction])
        df      = pd.concat([df, new_row], ignore_index=True)

        # Save updated transactions list
        df.to_csv(TRANSACTIONS_FILE, index=False)

        # Merge into cleaned data so analysis stays up to date
        merge_with_cleaned(new_row)

        return jsonify({
            'message':       'Transaction recorded successfully!',
            'transaction':   transaction,
            'total_records': len(df)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@transactions_bp.route('/all', methods=['GET'])
def get_transactions():
    """
    GET /api/transactions/all
    Returns all manually recorded transactions as a list,
    along with the total count.
    """
    df = load_transactions()
    return jsonify({
        'transactions': df.to_dict(orient='records'),
        'total':        len(df)
    }), 200


@transactions_bp.route('/delete/<int:index>', methods=['DELETE'])
def delete_transaction(index):
    """
    DELETE /api/transactions/delete/<index>
    Deletes a transaction by its row index in the CSV.

    Parameters:
        index (int): Zero-based row index of the transaction to delete
    """
    df = load_transactions()

    if index < 0 or index >= len(df):
        return jsonify({'error': 'Invalid transaction index'}), 400

    # Drop the row and reset index numbers
    df = df.drop(index=index).reset_index(drop=True)
    df.to_csv(TRANSACTIONS_FILE, index=False)

    return jsonify({'message': 'Transaction deleted successfully'}), 200