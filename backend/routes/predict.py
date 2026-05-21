from flask import Blueprint, request, jsonify
import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.ml.predict import predict_demand

predict_bp = Blueprint('predict', __name__)

@predict_bp.route('/', methods=['POST'])
def predict():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Required fields
    required = ['product', 'category', 'channel', 'unit_price', 'month']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400

    try:
        month        = int(data['month'])
        day_of_week  = int(data.get('day_of_week', datetime.now().weekday()))
        quarter      = (month - 1) // 3 + 1

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