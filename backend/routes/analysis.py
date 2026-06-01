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

@analysis_bp.route('/gender-breakdown', methods=['GET'])
def gender_breakdown():
    """
    GET /api/analysis/gender-breakdown
    Returns total revenue split by customer gender.
    Used for the gender doughnut chart.
    """
    df = load_cleaned_data()
    if df is None:
        return jsonify({'error': 'No data found'}), 400

    if 'Sex' not in df.columns:
        return jsonify({'error': 'No gender column found'}), 400

    breakdown = df.groupby('Sex')['Amount'].sum().reset_index()
    return jsonify(breakdown.to_dict(orient='records')), 200


@analysis_bp.route('/top-customers', methods=['GET'])
def top_customers():
    """
    GET /api/analysis/top-customers
    Returns the top 10 customers by total spending.
    Used for the horizontal bar chart.
    """
    df = load_cleaned_data()
    if df is None:
        return jsonify({'error': 'No data found'}), 400

    if 'Customer_Name' not in df.columns:
        return jsonify({'error': 'No customer column found'}), 400

    top = df.groupby('Customer_Name')['Amount'].sum() \
            .sort_values(ascending=False).head(10)
    return jsonify(top.reset_index().to_dict(orient='records')), 200


@analysis_bp.route('/day-of-week', methods=['GET'])
def day_of_week():
    """
    GET /api/analysis/day-of-week
    Returns total revenue grouped by day of week.
    Helps identify which days generate most sales.
    """
    df = load_cleaned_data()
    if df is None:
        return jsonify({'error': 'No data found'}), 400

    # Map day numbers to names
    day_names = {
        0: 'Monday',    1: 'Tuesday',  2: 'Wednesday',
        3: 'Thursday',  4: 'Friday',   5: 'Saturday',
        6: 'Sunday'
    }
    df['DayOfWeek'] = df['Date'].dt.dayofweek
    df['DayName']   = df['DayOfWeek'].map(day_names)
    result = df.groupby(['DayOfWeek', 'DayName'])['Amount'] \
               .sum().reset_index() \
               .sort_values('DayOfWeek')
    return jsonify(result[['DayName', 'Amount']].to_dict(orient='records')), 200


@analysis_bp.route('/monthly-quantity', methods=['GET'])
def monthly_quantity():
    """
    GET /api/analysis/monthly-quantity
    Returns total quantity sold per month.
    Shows volume trends separately from revenue trends.
    """
    df = load_cleaned_data()
    if df is None:
        return jsonify({'error': 'No data found'}), 400

    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    result = df.groupby('Month')['Quantity'].sum().reset_index()
    return jsonify(result.to_dict(orient='records')), 200


@analysis_bp.route('/product-quantity', methods=['GET'])
def product_quantity():
    """
    GET /api/analysis/product-quantity
    Returns top 10 products by quantity sold (not revenue).
    Shows volume leaders vs revenue leaders.
    """
    df = load_cleaned_data()
    if df is None:
        return jsonify({'error': 'No data found'}), 400

    top = df.groupby('Product')['Quantity'].sum() \
            .sort_values(ascending=False).head(10)
    return jsonify(top.reset_index().to_dict(orient='records')), 200


@analysis_bp.route('/extended-summary', methods=['GET'])
def extended_summary():
    """
    GET /api/analysis/extended-summary
    Returns extended business metrics including
    best month, best product, best category and
    total quantity sold.
    """
    df = load_cleaned_data()
    if df is None:
        return jsonify({'error': 'No data found'}), 400

    df['Month'] = df['Date'].dt.strftime('%B %Y')

    best_month    = df.groupby('Month')['Amount'].sum().idxmax()
    best_product  = df.groupby('Product')['Amount'].sum().idxmax()
    best_category = df.groupby('Category')['Amount'].sum().idxmax()
    best_channel  = df.groupby('Channel')['Amount'].sum().idxmax()
    total_qty     = int(df['Quantity'].sum())

    return jsonify({
        'best_month':    best_month,
        'best_product':  best_product,
        'best_category': best_category,
        'best_channel':  best_channel,
        'total_quantity': total_qty
    }), 200