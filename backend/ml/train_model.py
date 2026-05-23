# ============================================================
# ml/train_model.py — Machine Learning Model Training Script
# Loads the sales dataset, engineers features, trains a
# Random Forest model to predict product demand (Quantity),
# evaluates its performance, and saves the model and encoders.
# ============================================================

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
import pickle
import os


def train_model():
    """
    Full training pipeline:
    1. Load dataset
    2. Engineer features
    3. Encode categorical variables
    4. Split into train/test sets
    5. Train Random Forest model
    6. Evaluate performance
    7. Save model and encoders as .pkl files
    """

    # ── Load Dataset ─────────────────────────────────────────
    data_path = os.path.join(
        os.path.dirname(__file__), '..', '..', 'data', 'sample_dataset.csv'
    )
    df = pd.read_csv(data_path)

    # ── Feature Engineering ──────────────────────────────────
    # Extract time-based features from the Date column
    # These help the model learn seasonal and weekly patterns
    df['Date']      = pd.to_datetime(df['Date'])
    df['Month']     = df['Date'].dt.month       # 1-12
    df['DayOfWeek'] = df['Date'].dt.dayofweek   # 0=Monday, 6=Sunday
    df['Quarter']   = df['Date'].dt.quarter     # 1-4

    # ── Encode Categorical Columns ───────────────────────────
    # ML models require numerical input, so we convert
    # text categories into numbers using LabelEncoder
    le_product  = LabelEncoder()
    le_category = LabelEncoder()
    le_channel  = LabelEncoder()

    df['Product_Encoded']  = le_product.fit_transform(df['Product'])
    df['Category_Encoded'] = le_category.fit_transform(df['Category'])
    df['Channel_Encoded']  = le_channel.fit_transform(df['Channel'])

    # ── Define Features and Target ───────────────────────────
    # Features (X): inputs the model uses to make predictions
    # Target  (y): what we want the model to predict (Quantity sold)
    features = [
        'Product_Encoded',   # Which product
        'Category_Encoded',  # Which category
        'Channel_Encoded',   # Online or Onsite
        'Unit_Price',        # Price of the product
        'Month',             # Month of the year
        'DayOfWeek',         # Day of the week
        'Quarter'            # Quarter of the year
    ]
    target = 'Quantity'

    X = df[features]
    y = df[target]

    # ── Train / Test Split ───────────────────────────────────
    # 80% of data for training, 20% for testing
    # random_state=42 ensures reproducible results
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # ── Train the Model ──────────────────────────────────────
    # Random Forest builds multiple decision trees and averages
    # their predictions for better accuracy and stability
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # ── Evaluate Performance ─────────────────────────────────
    y_pred = model.predict(X_test)

    # MAE: average prediction error in units
    # R²:  how well the model explains variance (1.0 = perfect)
    mae = mean_absolute_error(y_test, y_pred)
    r2  = r2_score(y_test, y_pred)

    print(f"✅ Model trained successfully!")
    print(f"   Mean Absolute Error : {mae:.2f}")
    print(f"   R² Score            : {r2:.2f}")

    # ── Save Model and Encoders ──────────────────────────────
    # We save both the model and encoders so predictions later
    # use the exact same encoding mappings used during training
    models_dir = os.path.join(
        os.path.dirname(__file__), '..', '..', 'models'
    )
    os.makedirs(models_dir, exist_ok=True)

    with open(os.path.join(models_dir, 'demand_model.pkl'), 'wb') as f:
        pickle.dump(model, f)       # Save trained model

    with open(os.path.join(models_dir, 'le_product.pkl'), 'wb') as f:
        pickle.dump(le_product, f)  # Save product encoder

    with open(os.path.join(models_dir, 'le_category.pkl'), 'wb') as f:
        pickle.dump(le_category, f) # Save category encoder

    with open(os.path.join(models_dir, 'le_channel.pkl'), 'wb') as f:
        pickle.dump(le_channel, f)  # Save channel encoder

    print(f"✅ Model and encoders saved to /models/")
    return mae, r2


# Run training when script is executed directly
if __name__ == '__main__':
    train_model()