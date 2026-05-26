# ============================================================
# ml/predict.py — Demand Prediction Logic
#
# Loads the saved ML model and encoders from /models/,
# encodes the input product details, runs the prediction,
# and returns the predicted demand with restocking advice.
#
# This module is imported by routes/predict.py to serve
# the /api/predict/ endpoint.
# ============================================================

import pickle
import numpy as np
import os

# Path to the directory where trained model files are saved
MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'models')


def load_artifacts():
    """
    Loads the trained model and all label encoders from disk.
    These were saved during training in train_model.py.

    Returns:
        model       : Trained RandomForestRegressor
        le_product  : LabelEncoder for Product column
        le_category : LabelEncoder for Category column
        le_channel  : LabelEncoder for Channel column
    """
    with open(os.path.join(MODELS_DIR, 'demand_model.pkl'), 'rb') as f:
        model = pickle.load(f)
    with open(os.path.join(MODELS_DIR, 'le_product.pkl'), 'rb') as f:
        le_product = pickle.load(f)
    with open(os.path.join(MODELS_DIR, 'le_category.pkl'), 'rb') as f:
        le_category = pickle.load(f)
    with open(os.path.join(MODELS_DIR, 'le_channel.pkl'), 'rb') as f:
        le_channel = pickle.load(f)

    return model, le_product, le_category, le_channel


def safe_encode(encoder, value):
    """
    Encodes a single value using a fitted LabelEncoder.
    Returns 0 for values not seen during training (unseen labels)
    to prevent crashes when new product names are entered.

    Parameters:
        encoder : A fitted LabelEncoder instance
        value   : The string value to encode

    Returns:
        int: Encoded integer, or 0 if value is unknown
    """
    if value in encoder.classes_:
        return encoder.transform([value])[0]
    return 0  # Default encoding for unseen labels


def predict_demand(product, category, channel,
                   unit_price, month, day_of_week, quarter):
    """
    Runs a demand prediction for a given product and context.

    Takes product details as inputs, encodes them using the
    saved encoders, builds the feature array, and passes it
    through the trained Random Forest model.

    Parameters:
        product     (str)  : Product name
        category    (str)  : Product category
        channel     (str)  : 'Online' or 'Onsite'
        unit_price  (float): Price per unit in FCFA
        month       (int)  : Month number (1-12)
        day_of_week (int)  : Day of week (0=Monday, 6=Sunday)
        quarter     (int)  : Quarter (1-4)

    Returns:
        dict: Prediction result with restock advice
    """
    model, le_product, le_category, le_channel = load_artifacts()

    # Encode categorical inputs to numbers using saved encoders
    product_enc  = safe_encode(le_product,  product)
    category_enc = safe_encode(le_category, category)
    channel_enc  = safe_encode(le_channel,  channel)

    # Build feature array in exact same order as during training
    features = np.array([[
        product_enc,
        category_enc,
        channel_enc,
        unit_price,
        month,
        day_of_week,
        quarter
    ]])

    # Run the prediction
    prediction = model.predict(features)[0]

    return {
        'product':          product,
        'category':         category,
        'channel':          channel,
        'month':            month,
        'predicted_demand': round(float(prediction), 2),
        'restock_advice':   get_restock_advice(prediction)
    }


def get_restock_advice(predicted_demand):
    """
    Converts a numeric demand prediction into a human-readable
    restocking recommendation using threshold rules.

    Thresholds:
        >= 8 units : High demand  → restock immediately
        >= 5 units : Moderate     → restock soon
        >= 2 units : Low          → restock in small qty
        <  2 units : Very low     → consider promotions

    Parameters:
        predicted_demand (float): Predicted quantity to be sold

    Returns:
        str: Restocking advice message with emoji indicator
    """
    if predicted_demand >= 8:
        return '🔴 High demand expected — restock immediately with large quantities.'
    elif predicted_demand >= 5:
        return '🟡 Moderate demand expected — restock soon with normal quantities.'
    elif predicted_demand >= 2:
        return '🟢 Low demand expected — restock in small quantities.'
    else:
        return '⚪ Very low demand — consider running a promotion to boost sales.'