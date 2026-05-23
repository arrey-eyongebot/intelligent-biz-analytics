# ============================================================
# ml/predict.py — Demand Prediction Logic
# Loads the saved ML model and encoders, processes input data,
# runs a prediction, and returns the result with restock advice.
# ============================================================

import pickle
import numpy as np
import os

# Path to the saved models directory
MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'models')


def load_artifacts():
    """
    Loads the trained model and all label encoders from disk.
    These were saved during training in train_model.py.
    Returns: model, le_product, le_category, le_channel
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


def predict_demand(product, category, channel, unit_price, month, day_of_week, quarter):
    """
    Takes product details as input, encodes them, runs the ML
    model, and returns the predicted demand with restock advice.

    Parameters:
        product     (str): Product name
        category    (str): Product category
        channel     (str): Sales channel (Online/Onsite)
        unit_price  (float): Price per unit
        month       (int): Month number (1-12)
        day_of_week (int): Day of week (0=Monday)
        quarter     (int): Quarter (1-4)

    Returns:
        dict with prediction details and restock advice
    """
    model, le_product, le_category, le_channel = load_artifacts()

    def safe_encode(encoder, value):
        """
        Encodes a value using a fitted LabelEncoder.
        Returns 0 for unseen labels to avoid crashes on new data.
        """
        if value in encoder.classes_:
            return encoder.transform([value])[0]
        return 0  # Default for unknown labels

    # Encode the categorical inputs into numbers
    product_enc  = safe_encode(le_product,  product)
    category_enc = safe_encode(le_category, category)
    channel_enc  = safe_encode(le_channel,  channel)

    # Build the feature array in the same order used during training
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
        'restock_advice':   restock_advice(prediction)
    }


def restock_advice(predicted_demand):
    """
    Converts a numeric demand prediction into a human-readable
    restocking recommendation based on defined thresholds.
    """
    if predicted_demand >= 8:
        return '🔴 High demand expected — restock immediately with large quantities.'
    elif predicted_demand >= 5:
        return '🟡 Moderate demand expected — restock soon with normal quantities.'
    elif predicted_demand >= 2:
        return '🟢 Low demand expected — restock in small quantities.'
    else:
        return '⚪ Very low demand — consider running a promotion to boost sales.'