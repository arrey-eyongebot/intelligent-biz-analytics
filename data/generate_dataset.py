import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Seed for reproducibility
np.random.seed(42)
random.seed(42)

# Sample data pools
customer_names = [
    "Ambe John", "Ngozi Fatima", "Tabi Ernest", "Mbah Grace", "Fon Peter",
    "Bih Sandra", "Nkeng Paul", "Awah Mary", "Tita George", "Nfor Alice",
    "Mbarga Felix", "Eyong Rita", "Agbor Samuel", "Ndip Helen", "Besong Eric",
    "Achu Cynthia", "Mbom David", "Njoku Rose", "Tanyi Victor", "Obi Stella"
]

sexes = ["Male", "Female"]

products = {
    "Electronics":  ["Phone Charger", "Earphones", "USB Cable", "Power Bank", "Bluetooth Speaker"],
    "Groceries":    ["Rice (5kg)", "Cooking Oil", "Sugar", "Flour", "Tomato Paste"],
    "Clothing":     ["T-Shirt", "Jeans", "Dress", "Sneakers", "Cap"],
    "Stationery":   ["Notebook", "Pen Set", "Stapler", "Printer Paper", "Calculator"],
    "Cosmetics":    ["Face Cream", "Hair Oil", "Lipstick", "Perfume", "Lotion"]
}

unit_prices = {
    "Phone Charger": 2500, "Earphones": 3000, "USB Cable": 1500,
    "Power Bank": 15000, "Bluetooth Speaker": 20000,
    "Rice (5kg)": 3500, "Cooking Oil": 2000, "Sugar": 1200,
    "Flour": 1800, "Tomato Paste": 500,
    "T-Shirt": 3000, "Jeans": 8000, "Dress": 7500,
    "Sneakers": 12000, "Cap": 2000,
    "Notebook": 500, "Pen Set": 800, "Stapler": 2500,
    "Printer Paper": 3000, "Calculator": 5000,
    "Face Cream": 3500, "Hair Oil": 2500, "Lipstick": 2000,
    "Perfume": 8000, "Lotion": 1800
}

channels = ["Online", "Onsite"]

# Generate 500 rows
rows = []
start_date = datetime(2024, 1, 1)

for i in range(500):
    category = random.choice(list(products.keys()))
    product = random.choice(products[category])
    unit_price = unit_prices[product]
    quantity = random.randint(1, 10)
    amount = unit_price * quantity
    date = start_date + timedelta(days=random.randint(0, 364))
    customer = random.choice(customer_names)
    sex = random.choice(sexes)
    channel = random.choice(channels)

    rows.append({
        "Customer_Name": customer,
        "Sex": sex,
        "Product": product,
        "Category": category,
        "Quantity": quantity,
        "Date": date.strftime("%Y-%m-%d"),
        "Unit_Price": unit_price,
        "Amount": amount,
        "Channel": channel
    })

# Create DataFrame and save
df = pd.DataFrame(rows)
df.to_csv("data/sample_dataset.csv", index=False)
print("✅ Dataset generated successfully!")
print(f"Shape: {df.shape}")
print(df.head())
