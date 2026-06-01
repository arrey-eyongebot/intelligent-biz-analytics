# ============================================================
# routes/advisory.py — AI-Powered Business Advisory Chatbot
#
# This module powers the chatbot on the advisory page.
# It uses the Anthropic Claude API to answer business questions
# based on the user's actual uploaded sales data.
#
# The chatbot has TWO main skills:
#
# SKILL 1 — BUSINESS ADVISOR:
#   Answers questions about sales performance, restocking,
#   marketing strategies, and business growth using the
#   actual numbers from the uploaded sales data.
#
# SKILL 2 — COLUMN MAPPING HELPER:
#   If a user pastes their column names or asks for help
#   with data mapping, the chatbot explains which system
#   column each one should map to and guides the user.
#
# The full conversation history is sent with each request
# so the chatbot remembers what was said earlier in the chat.
#
# Endpoint:
#   POST /api/advisory/chat
# ============================================================

from flask import Blueprint, request, jsonify
import pandas as pd
import anthropic
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.config import UPLOAD_FOLDER

# Create the advisory blueprint
advisory_bp = Blueprint('advisory', __name__)

# Initialize the Anthropic client
# It automatically reads ANTHROPIC_API_KEY from environment variables
client = anthropic.Anthropic(
    api_key=os.environ.get('ANTHROPIC_API_KEY')
)


def load_cleaned_data():
    """
    Loads the cleaned sales CSV into a DataFrame.
    Returns None if no data has been uploaded yet.
    """
    path = os.path.join(UPLOAD_FOLDER, 'cleaned_data.csv')
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    df['Date'] = pd.to_datetime(df['Date'])
    return df


def build_data_summary(df):
    """
    Builds a structured text summary of key business metrics
    from the sales DataFrame. This summary is injected into
    the AI system prompt so Claude has specific knowledge
    about the business when answering questions.

    Parameters:
        df (DataFrame): Cleaned sales data

    Returns:
        summary (str): Formatted business metrics string
    """
    # Compute key metrics
    total_revenue      = df['Amount'].sum()
    total_transactions = len(df)
    top_product        = df.groupby('Product')['Amount'].sum().idxmax()
    slow_product       = df.groupby('Product')['Quantity'].sum().idxmin()
    best_channel       = df.groupby('Channel')['Amount'].sum().idxmax()
    best_category      = df.groupby('Category')['Amount'].sum().idxmax()

    # Find the best performing month
    df['Month'] = df['Date'].dt.strftime('%B %Y')
    best_month  = df.groupby('Month')['Amount'].sum().idxmax()

    # Top 5 products by revenue
    top5     = df.groupby('Product')['Amount'].sum() \
                 .sort_values(ascending=False).head(5)
    top5_str = ', '.join([f"{p} ({a:,.0f} FCFA)" for p, a in top5.items()])

    # Revenue breakdown by category
    cat_bd  = df.groupby('Category')['Amount'].sum() \
                .sort_values(ascending=False)
    cat_str = ', '.join([f"{c}: {a:,.0f} FCFA" for c, a in cat_bd.items()])

    # Format summary as readable text block
    summary = f"""
    BUSINESS SALES DATA SUMMARY:
    - Total Revenue        : {total_revenue:,.0f} FCFA
    - Total Transactions   : {total_transactions}
    - Best Selling Product : {top_product}
    - Slowest Product      : {slow_product}
    - Best Sales Channel   : {best_channel}
    - Best Month           : {best_month}
    - Top Category         : {best_category}
    - Top 5 Products       : {top5_str}
    - Category Breakdown   : {cat_str}
    """
    return summary


@advisory_bp.route('/chat', methods=['POST'])
def chat():
    """
    POST /api/advisory/chat
    Receives a user message and conversation history,
    builds a context-aware prompt with the business data,
    calls the Claude API, and returns the AI response.

    Request body:
    {
        "message": "Which product should I restock first?",
        "history": [
            {"role": "user",      "content": "..."},
            {"role": "assistant", "content": "..."}
        ]
    }

    Returns:
    {
        "reply": "Based on your data, I recommend restocking..."
    }
    """
    data = request.get_json()

    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400

    user_message = data['message']
    history      = data.get('history', [])  # Previous conversation turns

    # Load the business sales data for context
    df = load_cleaned_data()

    # If no data uploaded yet, guide the user
    if df is None:
        return jsonify({
            'reply': (
                'Hello! I am your AI business advisor. '
                'It looks like you have not uploaded any sales data yet. '
                'Please go to the Home page and upload your sales file first, '
                'then come back and I can give you personalized advice based '
                'on your actual business data!'
            )
        }), 200

    # Build the business data summary for the AI context
    data_summary = build_data_summary(df)

    # ── System Prompt ────────────────────────────────────────
    # This tells Claude its role, gives it the business data,
    # and explains both skills it should perform.
    system_prompt = f"""
    You are an intelligent business advisory chatbot for small and medium
    businesses in Cameroon. You have two main skills:

    SKILL 1 — BUSINESS ADVISOR:
    You have access to the business owner's actual sales data (shown below).
    Use this data to answer questions about their business performance.
    Give clear, practical, and actionable advice. Refer to actual products,
    categories, channels, and numbers from the data. Use simple language
    that a non-technical business owner can easily understand.
    Format responses clearly using bullet points where appropriate.
    Keep responses concise but informative.

    SKILL 2 — COLUMN MAPPING HELPER:
    If the user pastes or describes their data column names and asks for
    help mapping them, analyze the column names and suggest which system
    column each one maps to from this list:
    Customer_Name, Sex, Product, Category, Quantity, Date,
    Unit_Price, Amount, Channel.

    For example if they say their columns are:
    "Item, Selling_Price, Qty, Date, Store_Type"
    Respond with:
    - Item          → Product
    - Selling_Price → Unit_Price
    - Qty           → Quantity
    - Date          → Date
    - Store_Type    → Channel
    Then tell them to go to the Home page upload section and use
    the column mapping dropdowns to apply these mappings.

    Always be friendly, encouraging, and helpful.

    Here is the current business sales data you should use:
    {data_summary}
    """

    # Build messages list including conversation history
    # This gives the AI memory of the current chat session
    messages = history + [
        {'role': 'user', 'content': user_message}
    ]

    try:
        # Call the Anthropic Claude API
        response = client.messages.create(
            model      = 'claude-sonnet-4-20250514',
            max_tokens = 1024,
            system     = system_prompt,
            messages   = messages
        )

        # Extract the text from the response
        reply = response.content[0].text
        return jsonify({'reply': reply}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500