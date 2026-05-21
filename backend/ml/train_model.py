import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
import pickle
import os

def train_model():
    # Load dataset
    data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'sample_dataset.csv')
    df = pd.read_csv(data_path)

    # ── Feature Engineering ──────────────────────────────
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month']      = df['Date'].dt.month
    df['DayOfWeek']  = df['Date'].dt.dayofweek
    df['Quarter']    = df['Date'].dt.quarter

    # Encode categorical columns
    le_product  = LabelEncoder()
    le_category = LabelEncoder()
    le_channel  = LabelEncoder()

    df['Product_Encoded']  = le_product.fit_transform(df['Product'])
    df['Category_Encoded'] = le_category.fit_transform(df['Category'])
    df['Channel_Encoded']  = le_channel.fit_transform(df['Channel'])

    # ── Features & Target ────────────────────────────────
    features = [
        'Product_Encoded',
        'Category_Encoded',
        'Channel_Encoded',
        'Unit_Price',
        'Month',
        'DayOfWeek',
        'Quarter'
    ]
    target = 'Quantity'

    X = df[features]
    y = df[target]

    # ── Train / Test Split ───────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # ── Train Model ──────────────────────────────────────
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # ── Evaluate ─────────────────────────────────────────
    y_pred = model.predict(X_test)
    mae    = mean_absolute_error(y_test, y_pred)
    r2     = r2_score(y_test, y_pred)

    print(f"✅ Model trained successfully!")
    print(f"   Mean Absolute Error : {mae:.2f}")
    print(f"   R² Score            : {r2:.2f}")

    # ── Save Model & Encoders ────────────────────────────
    models_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'models')
    os.makedirs(models_dir, exist_ok=True)

    with open(os.path.join(models_dir, 'demand_model.pkl'),    'wb') as f:
        pickle.dump(model, f)
    with open(os.path.join(models_dir, 'le_product.pkl'),      'wb') as f:
        pickle.dump(le_product, f)
    with open(os.path.join(models_dir, 'le_category.pkl'),     'wb') as f:
        pickle.dump(le_category, f)
    with open(os.path.join(models_dir, 'le_channel.pkl'),      'wb') as f:
        pickle.dump(le_channel, f)

    print(f"✅ Model and encoders saved to /models/")
    return mae, r2

if __name__ == '__main__':
    train_model()