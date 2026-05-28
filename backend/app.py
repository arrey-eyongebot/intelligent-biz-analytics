# ============================================================
# app.py — Main Flask Application Entry Point
#
# Creates the Flask app, configures sessions, enables CORS,
# and registers all route blueprints.
# ============================================================

from flask import Flask
from flask_cors import CORS
from routes.upload       import upload_bp
from routes.analysis     import analysis_bp
from routes.advisory     import advisory_bp
from routes.predict      import predict_bp
from routes.transactions import transactions_bp
from routes.auth         import auth_bp
import os

app = Flask(__name__)

# ── Secret Key for Sessions ──────────────────────────────────
# Used to sign session cookies securely.
# In production this should be a long random secret string
# stored in an environment variable.
app.secret_key = os.environ.get('SECRET_KEY', 'bizanalytics-secret-key-2025')

# ── Enable CORS with session support ─────────────────────────
# supports_credentials=True is required for session cookies
# to work across different ports (frontend 5500, backend 5000)
CORS(app, supports_credentials=True)

# ── Register All Blueprints ───────────────────────────────────
app.register_blueprint(auth_bp,          url_prefix='/api/auth')
app.register_blueprint(upload_bp,        url_prefix='/api/upload')
app.register_blueprint(analysis_bp,      url_prefix='/api/analysis')
app.register_blueprint(advisory_bp,      url_prefix='/api/advisory')
app.register_blueprint(predict_bp,       url_prefix='/api/predict')
app.register_blueprint(transactions_bp,  url_prefix='/api/transactions')

if __name__ == '__main__':
    app.run(debug=True)