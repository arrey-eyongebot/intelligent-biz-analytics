# ============================================================
# app.py — Main Entry Point for the Flask Application
#
# This file is the starting point of the entire backend.
# It creates the Flask app, enables CORS so the frontend
# can communicate with the backend across different ports,
# and registers all route blueprints (groups of endpoints).
#
# To run the app: python app.py
# The server will start at http://127.0.0.1:5000
# ============================================================

from flask import Flask
from flask_cors import CORS

# Import all route blueprints from the routes folder
from routes.upload       import upload_bp        # File upload & column mapping
from routes.analysis     import analysis_bp      # Sales data analysis
from routes.advisory     import advisory_bp      # AI chatbot advisory
from routes.predict      import predict_bp       # ML demand prediction
from routes.transactions import transactions_bp  # Manual transaction recording

# ── Create Flask App Instance ────────────────────────────────
app = Flask(__name__)

# ── Enable CORS ──────────────────────────────────────────────
# Without this, the browser blocks requests from the frontend
# (running on port 5500) to the backend (running on port 5000)
CORS(app)

# ── Register Blueprints ──────────────────────────────────────
# Each blueprint handles a specific group of API endpoints.
# url_prefix defines the base URL path for each group.
app.register_blueprint(upload_bp,        url_prefix='/api/upload')
app.register_blueprint(analysis_bp,      url_prefix='/api/analysis')
app.register_blueprint(advisory_bp,      url_prefix='/api/advisory')
app.register_blueprint(predict_bp,       url_prefix='/api/predict')
app.register_blueprint(transactions_bp,  url_prefix='/api/transactions')

# ── Start the Server ─────────────────────────────────────────
# debug=True enables auto-reload on changes and detailed errors
if __name__ == '__main__':
    app.run(debug=True)