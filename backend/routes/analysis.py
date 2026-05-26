# ============================================================
# routes/analysis.py — Sales Data Analysis Endpoints
#
# Provides API endpoints that read the cleaned sales data
# and return computed insights for the dashboard charts.
#
# All endpoints load data from the cleaned_data.csv file
# that was saved during the upload/confirm process.
#
# Endpoints:
#   GET /api/analysis/summary            — Key business metrics
#   GET /api/analysis/top-products       — Top 10 products by revenue
#   GET /api/analysis/sales-trend        — Monthly revenue trend
#   GET /api/analysis/channel-breakdown  — Online vs Onsite split
#   GET /api/analysis/category-performance — Revenue by category
# ============================================================

from flask import Blueprint, jsonify
import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.config import UPLOAD_FOLDER

# Create the analysis blueprint
analysis_bp = Blueprint('analysis', __name__)


def load_cleaned_data():
    """
    Helper: loads the cleaned CSV into a DataFrame.
    Returns None if no data has been uploaded yet.
    Ensures the Date column is parsed as datetime.
    """
    path = os.path.join(UPLOAD_FOLDER, 'cleaned_data.csv')
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    df['Date'] = pd.to_datetime(df['Date'])
    return df


@analysis_bp.route('/summary', methods=['GET'])
def summary():
    """
    GET /api/analysis/summary
    Returns high-level business performance metrics:
    - Total revenue (sum of all Amount values)
    - Total number of transactions (rows)
    - Number of unique products sold
    - Number of unique customers
    - Average value per transaction
    """
    df = load_cleaned_data()
    if df is None:
        return jsonify({'error': 'No data found. Please upload a file first.'}), 400

    return jsonify({
        'total_sales':           float(df['Amount'].sum()),
        'total_transactions':    int(len(df)),
        'total_products':        int(df['Product'].nunique()),
        'total_customers':       int(df['Customer_Name'].nunique())
                                 if 'Customer_Name' in df.columns else 0,
        'avg_transaction_value': float(df['Amount'].mean())
    }), 200


@analysis_bp.route('/top-products', methods=['GET'])
def top_products():
    """
    GET /api/analysis/top-products
    Returns the top 10 products ranked by total revenue.
    Groups all transactions by Product, sums their Amount,
    sorts descending, and returns the top 10.
    Used for the bar chart on the dashboard.
    """
    df = load_cleaned_data()
    if df is None:
        return jsonify({'error': 'No data found'}), 400

    top = df.groupby('Product')['Amount'].sum() \
            .sort_values(ascending=False).head(10)
    return jsonify(top.reset_index().to_dict(orient='records')), 200


@analysis_bp.route('/sales-trend', methods=['GET'])
def sales_trend():
    """
    GET /api/analysis/sales-trend
    Returns total revenue grouped by month (e.g. '2024-01').
    Used for the monthly line chart on the dashboard.
    """
    df = load_cleaned_data()
    if df is None:
        return jsonify({'error': 'No data found'}), 400

    # Convert Date to year-month period string (e.g. "2024-01")
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    trend = df.groupby('Month')['Amount'].sum().reset_index()
    return jsonify(trend.to_dict(orient='records')), 200


@analysis_bp.route('/channel-breakdown', methods=['GET'])
def channel_breakdown():
    """
    GET /api/analysis/channel-breakdown
    Returns total revenue split by sales channel (Online vs Onsite).
    Used for the doughnut chart on the dashboard.
    """
    df = load_cleaned_data()
    if df is None:
        return jsonify({'error': 'No data found'}), 400

    breakdown = df.groupby('Channel')['Amount'].sum().reset_index()
    return jsonify(breakdown.to_dict(orient='records')), 200


@analysis_bp.route('/category-performance', methods=['GET'])
def category_performance():
    """
    GET /api/analysis/category-performance
    Returns total revenue per product category, sorted highest first.
    Used for the category bar chart on the dashboard.
    """
    df = load_cleaned_data()
    if df is None:
        return jsonify({'error': 'No data found'}), 400

    perf = df.groupby('Category')['Amount'].sum() \
             .sort_values(ascending=False).reset_index()
    return jsonify(perf.to_dict(orient='records')), 200