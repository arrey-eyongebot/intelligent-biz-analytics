# ============================================================
# app.py — Main Flask Application Entry Point
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

# Secret key for signing session cookies
app.secret_key = os.environ.get('SECRET_KEY', 'bizanalytics-secret-key-2025')

# Session cookie settings
# These are critical for sessions to work across ports
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE']   = False  # False for local development
app.config['SESSION_COOKIE_HTTPONLY'] = True

# Enable CORS with credentials support
CCORS(app,
     supports_credentials=True,
     origins=['http://127.0.0.1:5500',
              'http://localhost:5500',
              'http://127.0.0.1:5501',
              'http://localhost:5501',
              'http://127.0.0.1:3000',
              'http://localhost:3000',
              'http://127.0.0.1:5000',
              'null'])
# Register all blueprints
app.register_blueprint(auth_bp,          url_prefix='/api/auth')
app.register_blueprint(upload_bp,        url_prefix='/api/upload')
app.register_blueprint(analysis_bp,      url_prefix='/api/analysis')
app.register_blueprint(advisory_bp,      url_prefix='/api/advisory')
app.register_blueprint(predict_bp,       url_prefix='/api/predict')
app.register_blueprint(transactions_bp,  url_prefix='/api/transactions')

if __name__ == '__main__':
    app.run(debug=True)