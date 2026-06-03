# ============================================================
# app.py — Production-Ready Flask Application Entry Point
#
# Configured for both local development and cloud deployment.
# Reads environment variables for sensitive configuration.
# Serves the frontend statically through Flask so only
# one server is needed in production.
# ============================================================

from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables from .env file
# In production these come from Render environment settings
load_dotenv()

# Import all route blueprints
from routes.upload       import upload_bp
from routes.analysis     import analysis_bp
from routes.advisory     import advisory_bp
from routes.predict      import predict_bp
from routes.transactions import transactions_bp
from routes.auth         import auth_bp

# ── Create Flask App ──────────────────────────────────────────
# static_folder points to the frontend directory
# so Flask can serve HTML, CSS and JS files directly
app = Flask(__name__,
            static_folder=os.path.join('..', 'frontend'),
            static_url_path='')

# ── Secret Key ────────────────────────────────────────────────
app.secret_key = os.environ.get('SECRET_KEY', 'bizanalytics-secret-2025')

# ── Session Cookie Config ─────────────────────────────────────
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE']   = False
app.config['SESSION_COOKIE_HTTPONLY'] = True

# ── CORS ──────────────────────────────────────────────────────
# Allow requests from any origin in production
CORS(app, supports_credentials=True)

# ── Serve Frontend Pages ──────────────────────────────────────
@app.route('/')
def index():
    """Serve the login page as the app entry point."""
    return send_from_directory(
        os.path.join('..', 'frontend'), 'login.html'
    )

@app.route('/<path:path>')
def serve_static(path):
    """
    Serve any frontend file (HTML, CSS, JS, images).
    This means Flask handles both the API and the frontend.
    """
    return send_from_directory(
        os.path.join('..', 'frontend'), path
    )

# ── Register All Blueprints ───────────────────────────────────
app.register_blueprint(auth_bp,          url_prefix='/api/auth')
app.register_blueprint(upload_bp,        url_prefix='/api/upload')
app.register_blueprint(analysis_bp,      url_prefix='/api/analysis')
app.register_blueprint(advisory_bp,      url_prefix='/api/advisory')
app.register_blueprint(predict_bp,       url_prefix='/api/predict')
app.register_blueprint(transactions_bp,  url_prefix='/api/transactions')

# ── Run App ───────────────────────────────────────────────────
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)