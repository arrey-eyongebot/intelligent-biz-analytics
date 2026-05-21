from flask import Blueprint, jsonify
import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.config import UPLOAD_FOLDER

analysis_bp = Blueprint('analysis', __name__)

def load_cleaned_data():
    path = os.path.join(UPLOAD_FOLDER, 'cleaned_data.csv')
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

@analysis_bp.route('/summary', methods=['GET'])
def summary():
    df = load_cleaned_data()
    if df is None:
        return jsonify({'error': 'No data found. Please upload a file first.'}), 400

    summary_data = {
        'total_sales': float(df['Amount'].sum()),
        'total_transactions': int(len(df)),
        'total_products': int(df['Product'].nunique()),
        'total_customers': int(df['Customer_Name'].nunique()) if 'Customer_Name' in df.columns else 0,
        'avg_transaction_value': float(df['Amount'].mean())
    }
    return jsonify(summary_data), 200


@analysis_bp.route('/top-products', methods=['GET'])
def top_products():
    df = load_cleaned_data()
    if df is None:
        return jsonify({'error': 'No data found'}), 400

    top = df.groupby('Product')['Amount'].sum()\
            .sort_values(ascending=False).head(10)
    return jsonify(top.reset_index().to_dict(orient='records')), 200


@analysis_bp.route('/sales-trend', methods=['GET'])
def sales_trend():
    df = load_cleaned_data()
    if df is None:
        return jsonify({'error': 'No data found'}), 400

    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    trend = df.groupby('Month')['Amount'].sum().reset_index()
    return jsonify(trend.to_dict(orient='records')), 200


@analysis_bp.route('/channel-breakdown', methods=['GET'])
def channel_breakdown():
    df = load_cleaned_data()
    if df is None:
        return jsonify({'error': 'No data found'}), 400

    breakdown = df.groupby('Channel')['Amount'].sum().reset_index()
    return jsonify(breakdown.to_dict(orient='records')), 200


@analysis_bp.route('/category-performance', methods=['GET'])
def category_performance():
    df = load_cleaned_data()
    if df is None:
        return jsonify({'error': 'No data found'}), 400

    perf = df.groupby('Category')['Amount'].sum()\
             .sort_values(ascending=False).reset_index()
    return jsonify(perf.to_dict(orient='records')), 200