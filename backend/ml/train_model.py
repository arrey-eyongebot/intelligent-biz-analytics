# ============================================================
# ml/train_model.py — ML Model Training Script
#
# This script trains a Random Forest machine learning model
# to predict product demand (Quantity sold) based on features
# extracted from the sales dataset.
#
# Training Pipeline:
# 1. Load the sample sales dataset
# 2. Engineer time-based features from the Date column
# 3. Encode categorical columns into numbers
# 4. Split data into training and testing sets (80/20)
# 5. Train a Random Forest Regressor model
# 6. Evaluate with MAE and R² score
# 7. Save the model and encoders as .pkl files
#
# Run this script once before starting the backend:
#   python backend/ml/train_model.py
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
    Full training pipeline for the demand prediction model.
    Saves trained model and encoders to the /models/ directory.

    Returns:
        mae (float): Mean Absolute Error on the test set
        r2  (float): R² Score on the test set
    """

    # ── Step 1: Load Dataset ─────────────────────────────────
    data_path = os.path.join(
        os.path.dirname(__file__), '..', '..', 'data', 'sample_dataset.csv'
    )
    df = pd.read_csv(data_path)

    # ── Step 2: Engineer Time Features ───────────────────────
    # Extract useful time patterns from the Date column.
    # These help the model learn seasonal and weekly demand trends.
    df['Date']      = pd.to_datetime(df['Date'])
    df['Month']     = df['Date'].dt.month       # 1 = January ... 12 = December
    df['DayOfWeek'] = df['Date'].dt.dayofweek   # 0 = Monday  ... 6 = Sunday
    df['Quarter']   = df['Date'].dt.quarter     # 1 = Jan-Mar ... 4 = Oct-Dec

    # ── Step 3: Encode Categorical Columns ───────────────────
    # ML models only work with numbers, not text.
    # LabelEncoder converts each unique text value to an integer.
    # e.g. ["Electronics","Groceries","Clothing"] → [0, 1, 2]
    le_product  = LabelEncoder()
    le_category = LabelEncoder()
    le_channel  = LabelEncoder()

    df['Product_Encoded']  = le_product.fit_transform(df['Product'])
    df['Category_Encoded'] = le_category.fit_transform(df['Category'])
    df['Channel_Encoded']  = le_channel.fit_transform(df['Channel'])

    # ── Step 4: Define Features and Target ───────────────────
    # Features (X): the inputs given to the model for prediction
    # Target   (y): what the model learns to predict (Quantity)
    features = [
        'Product_Encoded',   # Which product is being sold
        'Category_Encoded',  # Which product category
        'Channel_Encoded',   # Online or Onsite
        'Unit_Price',        # Price per unit (affects demand)
        'Month',             # Time of year (seasonal patterns)
        'DayOfWeek',         # Day of week (weekly patterns)
        'Quarter'            # Quarter of year
    ]
    target = 'Quantity'

    X = df[features]
    y = df[target]

    # ── Step 5: Train/Test Split ──────────────────────────────
    # We train on 80% of data and test on the remaining 20%.
    # random_state=42 ensures reproducible results every run.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # ── Step 6: Train the Model ───────────────────────────────
    # Random Forest builds many decision trees and averages their
    # predictions, which gives better accuracy than a single tree.
    # n_estimators=100 means 100 trees are built.
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # ── Step 7: Evaluate Performance ─────────────────────────
    y_pred = model.predict(X_test)

    # MAE: average prediction error in units sold
    # Lower is better (0 would be perfect)
    mae = mean_absolute_error(y_test, y_pred)

    # R²: how well the model explains variance in demand
    # 1.0 = perfect, 0.0 = no better than guessing the mean
    r2  = r2_score(y_test, y_pred)

    print(f"✅ Model trained successfully!")
    print(f"   Mean Absolute Error : {mae:.2f} units")
    print(f"   R² Score            : {r2:.2f}")

    # ── Step 8: Save Model and Encoders ──────────────────────
    # We save the model AND encoders together because predictions
    # must use the exact same encoding as training.
    # If we re-encode at prediction time, the numbers would differ.
    models_dir = os.path.join(
        os.path.dirname(__file__), '..', '..', 'models'
    )
    os.makedirs(models_dir, exist_ok=True)

    # Save each artifact as a .pkl (pickle) binary file
    artifacts = {
        'demand_model.pkl': model,       # The trained Random Forest
        'le_product.pkl':   le_product,  # Product name encoder
        'le_category.pkl':  le_category, # Category encoder
        'le_channel.pkl':   le_channel   # Channel encoder
    }

    for filename, obj in artifacts.items():
        with open(os.path.join(models_dir, filename), 'wb') as f:
            pickle.dump(obj, f)

    print(f"✅ Model and encoders saved to /models/")
    return mae, r2


# Run training when executed directly
if __name__ == '__main__':
    train_model()