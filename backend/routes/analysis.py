# ============================================================
# routes/analysis.py — Sales Data Analysis Endpoints
# Provides multiple API endpoints that analyze the cleaned
# sales data and return insights for the dashboard charts.
# ============================================================

from flask import Blueprint, jsonify
import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.config import UPLOAD_FOLDER

# Create a Blueprint named 'analysis'
analysis_bp = Blueprint('analysis', __name__)


def load_cleaned_data():
    """
    Helper function to load the cleaned CSV data into a DataFrame.
    Returns None if no data has been uploaded yet.
    """
    path = os.path.join(UPLOAD_FOLDER, 'cleaned_data.csv')
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    df['Date'] = pd.to_datetime(df['Date'])  # Ensure Date is datetime type
    return df


@analysis_bp.route('/summary', methods=['GET'])
def summary():
    """
    GET /api/analysis/summary
    Returns high-level business metrics:
    total revenue, transactions, products, customers, average transaction.
    """
    df = load_cleaned_data()
    if df is None:
        return jsonify({'error': 'No data found. Please upload a file first.'}), 400

    summary_data = {
        'total_sales':          float(df['Amount'].sum()),         # Total revenue
        'total_transactions':   int(len(df)),                      # Number of sales
        'total_products':       int(df['Product'].nunique()),       # Unique products
        'total_customers':      int(df['Customer_Name'].nunique())  # Unique customers
                                if 'Customer_Name' in df.columns else 0,
        'avg_transaction_value': float(df['Amount'].mean())        # Average sale value
    }
    return jsonify(summary_data), 200


@analysis_bp.route('/top-products', methods=['GET'])
def top_products():
    """
    GET /api/analysis/top-products
    Returns the top 10 products ranked by total revenue generated.
    Used for the bar chart on the dashboard.
    """
    df = load_cleaned_data()
    if df is None:
        return jsonify({'error': 'No data found'}), 400

    # Group by product, sum revenue, sort descending, take top 10
    top = df.groupby('Product')['Amount'].sum() \
            .sort_values(ascending=False).head(10)
    return jsonify(top.reset_index().to_dict(orient='records')), 200


@analysis_bp.route('/sales-trend', methods=['GET'])
def sales_trend():
    """
    GET /api/analysis/sales-trend
    Returns total revenue grouped by month.
    Used for the line chart showing sales over time.
    """
    df = load_cleaned_data()
    if df is None:
        return jsonify({'error': 'No data found'}), 400

    # Extract year-month string from Date column (e.g. "2024-01")
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    trend = df.groupby('Month')['Amount'].sum().reset_index()
    return jsonify(trend.to_dict(orient='records')), 200


@analysis_bp.route('/channel-breakdown', methods=['GET'])
def channel_breakdown():
    """
    GET /api/analysis/channel-breakdown
    Returns revenue split between Online and Onsite channels.
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
    Returns revenue per product category sorted by highest revenue.
    Used for the category bar chart on the dashboard.
    """
    df = load_cleaned_data()
    if df is None:
        return jsonify({'error': 'No data found'}), 400

    perf = df.groupby('Category')['Amount'].sum() \
             .sort_values(ascending=False).reset_index()
    return jsonify(perf.to_dict(orient='records')), 200