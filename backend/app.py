# ============================================================
# app.py — Main entry point for the Flask application
# This file initializes the Flask app, enables CORS so the
# frontend can communicate with the backend, and registers
# all route blueprints (upload, analysis, advisory, predict).
# ============================================================

from flask import Flask
from flask_cors import CORS

# Import route blueprints from the routes folder
from routes.upload import upload_bp
from routes.analysis import analysis_bp
from routes.advisory import advisory_bp
from routes.predict import predict_bp

# Create the Flask application instance
app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS)
# This allows the frontend (running on a different port) to
# make requests to this backend without being blocked
CORS(app)

# ── Register Blueprints ──────────────────────────────────────
# Each blueprint handles a specific group of API endpoints.
# The url_prefix defines the base URL for each group.

app.register_blueprint(upload_bp,   url_prefix='/api/upload')   # File upload endpoints
app.register_blueprint(analysis_bp, url_prefix='/api/analysis') # Data analysis endpoints
app.register_blueprint(advisory_bp, url_prefix='/api/advisory') # Business advice endpoints
app.register_blueprint(predict_bp,  url_prefix='/api/predict')  # ML prediction endpoints

# ── Run the App ──────────────────────────────────────────────
# debug=True enables auto-reload on code changes and
# shows detailed error messages during development
if __name__ == '__main__':
    app.run(debug=True)