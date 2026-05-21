import pickle
import numpy as np
import os

# Paths
MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'models')

def load_artifacts():
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
    model, le_product, le_category, le_channel = load_artifacts()

    # Encode inputs safely
    def safe_encode(encoder, value):
        if value in encoder.classes_:
            return encoder.transform([value])[0]
        return 0  # default for unseen labels

    product_enc  = safe_encode(le_product,  product)
    category_enc = safe_encode(le_category, category)
    channel_enc  = safe_encode(le_channel,  channel)

    features = np.array([[
        product_enc,
        category_enc,
        channel_enc,
        unit_price,
        month,
        day_of_week,
        quarter
    ]])

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
    if predicted_demand >= 8:
        return '🔴 High demand expected — restock immediately with large quantities.'
    elif predicted_demand >= 5:
        return '🟡 Moderate demand expected — restock soon with normal quantities.'
    elif predicted_demand >= 2:
        return '🟢 Low demand expected — restock in small quantities.'
    else:
        return '⚪ Very low demand — consider running a promotion to boost sales.'