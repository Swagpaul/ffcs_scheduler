import os
import sys
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from flask_migrate import Migrate
from sqlalchemy.exc import OperationalError

from app.models.models import db
from app.routes.api import api_bp
from config import config_map

load_dotenv()

migrate = Migrate()

def create_app(config_name="default"):
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Configuration
    env_config = os.getenv('FLASK_ENV', config_name)
    app.config.from_object(config_map.get(env_config, config_map['default']))

    # Initialize Plugins
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Register Blueprints
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.route('/')
    def dashboard():
        return render_template('index.html')

    @app.route('/login')
    def login_page():
        return render_template('login.html')

    @app.route('/courses')
    def courses_page():
        return render_template('courses.html')

    @app.route('/generate')
    def generate_page():
        return render_template('generate.html')

    @app.route('/results')
    def results_page():
        return render_template('results.html')
        
    @app.errorhandler(OperationalError)
    def handle_db_connection_error(e):
        return jsonify({"error": "Database connection error. Please try again later.", "details": str(e)}), 500

    # Removed db.create_all() as migrations will be used instead.
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
