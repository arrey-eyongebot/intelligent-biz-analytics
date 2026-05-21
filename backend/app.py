from flask import Flask
from flask_cors import CORS
from routes.upload import upload_bp
from routes.analysis import analysis_bp
from routes.advisory import advisory_bp

app = Flask(__name__)
CORS(app)  # Allow frontend to communicate with backend

# Register blueprints (route modules)
app.register_blueprint(upload_bp, url_prefix='/api/upload')
app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
app.register_blueprint(advisory_bp, url_prefix='/api/advisory')

if __name__ == '__main__':
    app.run(debug=True)