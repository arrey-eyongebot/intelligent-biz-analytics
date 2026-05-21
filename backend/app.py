from flask import Flask
from flask_cors import CORS
from routes.upload import upload_bp
from routes.analysis import analysis_bp
from routes.advisory import advisory_bp
from routes.predict import predict_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(upload_bp,   url_prefix='/api/upload')
app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
app.register_blueprint(advisory_bp, url_prefix='/api/advisory')
app.register_blueprint(predict_bp,  url_prefix='/api/predict')

if __name__ == '__main__':
    app.run(debug=True)