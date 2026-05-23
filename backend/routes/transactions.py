# ============================================================
# routes/transactions.py — Manual Transaction Recording
# Allows business owners to record individual sales
# transactions directly through the web app.
# Transactions are saved and merged with existing data.
# ============================================================

from flask import Blueprint, request, jsonify
import pandas as pd
import os
from datetime import datetime
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.config import UPLOAD_FOLDER

transactions_bp = Blueprint('transactions', __name__)

# Path to the manually recorded transactions file
TRANSACTIONS_FILE = os.path.join(UPLOAD_FOLDER, 'manual_transactions.csv')

# Required columns for a valid transaction
REQUIRED_FIELDS = ['Product', 'Category', 'Quantity', 'Unit_Price', 'Channel']


def load_transactions():
    """Load existing manual transactions or return empty DataFrame."""
    if os.path.exists(TRANSACTIONS_FILE):
        return pd.read_csv(TRANSACTIONS_FILE)
    return pd.DataFrame(columns=[
        'Customer_Name', 'Sex', 'Product', 'Category',
        'Quantity', 'Date', 'Unit_Price', 'Amount', 'Channel'
    ])


def merge_with_cleaned(new_df):
    """
    Merges new transactions with existing cleaned data
    so all analysis includes both uploaded and recorded data.
    """
    cleaned_path = os.path.join(UPLOAD_FOLDER, 'cleaned_data.csv')
    if os.path.exists(cleaned_path):
        existing = pd.read_csv(cleaned_path)
        merged   = pd.concat([existing, new_df], ignore_index=True)
        merged.drop_duplicates(inplace=True)
        merged.to_csv(cleaned_path, index=False)


@transactions_bp.route('/add', methods=['POST'])
def add_transaction():
    """
    POST /api/transactions/add
    Records a single new sales transaction.

    Request body:
    {
        "Customer_Name": "Ambe John",
        "Sex": "Male",
        "Product": "Rice (5kg)",
        "Category": "Groceries",
        "Quantity": 3,
        "Unit_Price": 3500,
        "Channel": "Onsite",
        "Date": "2025-05-20"  (optional, defaults to today)
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Validate required fields
    for field in REQUIRED_FIELDS:
        if field not in data or not str(data[field]).strip():
            return jsonify({'error': f'Missing required field: {field}'}), 400

    try:
        # Calculate Amount if not provided
        quantity   = float(data['Quantity'])
        unit_price = float(data['Unit_Price'])
        amount     = quantity * unit_price

        # Build the transaction record
        transaction = {
            'Customer_Name': data.get('Customer_Name', 'Anonymous'),
            'Sex':           data.get('Sex', 'Unknown'),
            'Product':       str(data['Product']).strip().title(),
            'Category':      str(data['Category']).strip().title(),
            'Quantity':      quantity,
            'Date':          data.get('Date', datetime.now().strftime('%Y-%m-%d')),
            'Unit_Price':    unit_price,
            'Amount':        amount,
            'Channel':       str(data['Channel']).strip().title()
        }

        # Load existing transactions and append new one
        df = load_transactions()
        new_row = pd.DataFrame([transaction])
        df = pd.concat([df, new_row], ignore_index=True)

        # Save to manual transactions file
        df.to_csv(TRANSACTIONS_FILE, index=False)

        # Merge with cleaned data for analysis
        merge_with_cleaned(new_row)

        return jsonify({
            'message':     'Transaction recorded successfully!',
            'transaction': transaction,
            'total_records': len(df)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@transactions_bp.route('/all', methods=['GET'])
def get_transactions():
    """
    GET /api/transactions/all
    Returns all manually recorded transactions.
    """
    df = load_transactions()
    return jsonify({
        'transactions': df.to_dict(orient='records'),
        'total': len(df)
    }), 200


@transactions_bp.route('/delete/<int:index>', methods=['DELETE'])
def delete_transaction(index):
    """
    DELETE /api/transactions/delete/<index>
    Deletes a transaction by its row index.
    """
    df = load_transactions()
    if index < 0 or index >= len(df):
        return jsonify({'error': 'Invalid transaction index'}), 400

    df = df.drop(index=index).reset_index(drop=True)
    df.to_csv(TRANSACTIONS_FILE, index=False)
    return jsonify({'message': 'Transaction deleted successfully'}), 200