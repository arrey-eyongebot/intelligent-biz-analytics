# ============================================================
# routes/predict.py — ML Demand Prediction Endpoint
#
# Exposes an API endpoint that accepts product details,
# passes them to the trained ML model, and returns the
# predicted demand quantity along with restocking advice.
#
# The model was trained in ml/train_model.py and the
# prediction logic lives in ml/predict.py.
#
# Endpoint:
#   POST /api/predict/
# ============================================================

from flask import Blueprint, request, jsonify
from datetime import datetime
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.ml.predict import predict_demand

# Create the predict blueprint
predict_bp = Blueprint('predict', __name__)


@predict_bp.route('/', methods=['POST'])
def predict():
    """
    POST /api/predict/
    Accepts product details and returns predicted demand.

    Required request body fields:
    - product    (str)  : Product name
    - category   (str)  : Product category
    - channel    (str)  : Sales channel (Online or Onsite)
    - unit_price (float): Price per unit in FCFA
    - month      (int)  : Month number to predict for (1-12)

    Optional:
    - day_of_week (int) : Day of week 0=Monday (defaults to today)

    Returns:
    {
        "product":          "Rice (5kg)",
        "category":         "Groceries",
        "channel":          "Online",
        "month":            6,
        "predicted_demand": 5.43,
        "restock_advice":   "Moderate demand expected..."
    }
    """
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Validate all required fields are present
    required = ['product', 'category', 'channel', 'unit_price', 'month']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    try:
        # Parse and compute time features
        month       = int(data['month'])
        day_of_week = int(data.get('day_of_week', datetime.now().weekday()))
        quarter     = (month - 1) // 3 + 1  # 1-3=Q1, 4-6=Q2, 7-9=Q3, 10-12=Q4

        # Call the prediction function from ml/predict.py
        result = predict_demand(
            product     = data['product'],
            category    = data['category'],
            channel     = data['channel'],
            unit_price  = float(data['unit_price']),
            month       = month,
            day_of_week = day_of_week,
            quarter     = quarter
        )

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500