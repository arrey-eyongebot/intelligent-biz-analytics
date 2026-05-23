# ============================================================
# routes/advisory.py — Business Advisory Endpoint
# Analyzes the cleaned sales data using rule-based logic
# and generates actionable business recommendations.
# ============================================================

from flask import Blueprint, jsonify
import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.config import UPLOAD_FOLDER

# Create a Blueprint named 'advisory'
advisory_bp = Blueprint('advisory', __name__)


def load_cleaned_data():
    """
    Helper function to load the cleaned sales data.
    Returns None if no file has been uploaded yet.
    """
    path = os.path.join(UPLOAD_FOLDER, 'cleaned_data.csv')
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    df['Date'] = pd.to_datetime(df['Date'])
    return df


@advisory_bp.route('/recommendations', methods=['GET'])
def recommendations():
    """
    GET /api/advisory/recommendations
    Applies rule-based analysis to the sales data and returns
    a list of business advice cards covering:
    - Best selling product
    - Slow moving product
    - Best sales channel
    - Peak sales month
    - Top performing category
    """
    df = load_cleaned_data()
    if df is None:
        return jsonify({'error': 'No data found. Please upload a file first.'}), 400

    # List to collect all advice items
    advice = []

    # ── Rule 1: Top performing product ──────────────────────
    # Find the product with the highest total revenue
    top_product = df.groupby('Product')['Amount'].sum().idxmax()
    advice.append({
        'type': 'Top Product',
        'message': f'"{top_product}" is your best-selling product. '
                   f'Consider increasing its stock and promoting it more.'
    })

    # ── Rule 2: Slow moving product ─────────────────────────
    # Find the product with the lowest total quantity sold
    slow_product = df.groupby('Product')['Quantity'].sum().idxmin()
    advice.append({
        'type': 'Slow Moving Product',
        'message': f'"{slow_product}" has the lowest sales quantity. '
                   f'Consider running a discount or promotion to clear stock.'
    })

    # ── Rule 3: Best sales channel ──────────────────────────
    # Determine whether Online or Onsite generates more revenue
    best_channel = df.groupby('Channel')['Amount'].sum().idxmax()
    advice.append({
        'type': 'Best Channel',
        'message': f'Most of your revenue comes from "{best_channel}" sales. '
                   f'Focus more marketing efforts on this channel.'
    })

    # ── Rule 4: Peak sales month ────────────────────────────
    # Find the month with the highest total revenue
    df['Month'] = df['Date'].dt.strftime('%B %Y')
    best_month = df.groupby('Month')['Amount'].sum().idxmax()
    advice.append({
        'type': 'Peak Sales Period',
        'message': f'Your highest sales were recorded in "{best_month}". '
                   f'Plan your restocking and promotions before this period.'
    })

    # ── Rule 5: Top category ─────────────────────────────────
    # Find the product category generating the most revenue
    best_category = df.groupby('Category')['Amount'].sum().idxmax()
    advice.append({
        'type': 'Top Category',
        'message': f'"{best_category}" is your most profitable category. '
                   f'Consider expanding your product range in this category.'
    })

    return jsonify({'recommendations': advice}), 200