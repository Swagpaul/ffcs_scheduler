import os
import sys
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from flask_migrate import Migrate
from sqlalchemy.exc import OperationalError

# Locate and load the correct .env file
if getattr(sys, 'frozen', False):
    basedir = os.path.dirname(sys.executable)
    env_path = os.path.join(basedir, '.env')
    if not os.path.exists(env_path):
        app_data = os.environ.get('APPDATA') or os.environ.get('LOCALAPPDATA') or os.path.expanduser('~')
        env_path = os.path.join(app_data, 'FFCS-Scheduler', '.env')
else:
    basedir = os.path.dirname(os.path.abspath(__file__))
    basedir = os.path.dirname(basedir) # root folder
    env_path = os.path.join(basedir, '.env')

if os.path.exists(env_path):
    load_dotenv(env_path, override=True)
else:
    load_dotenv(override=True)

from app.models.models import db
from app.routes.api import api_bp
from config import config_map
migrate = Migrate()

def create_app(config_name="default"):
    # If running inside PyInstaller, set correct static/template paths
    if getattr(sys, 'frozen', False):
        # PyInstaller bundles files in sys._MEIPASS
        base_dir = sys._MEIPASS
        app = Flask(__name__,
                    template_folder=os.path.join(base_dir, 'app', 'templates'),
                    static_folder=os.path.join(base_dir, 'app', 'static'))
    else:
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

    # Automatically create SQLite tables and seed slots on startup
    with app.app_context():
        db.create_all()
        # Migration: Add priority column to course_offerings table if missing
        from sqlalchemy import text
        try:
            db.session.execute(text("SELECT priority FROM course_offerings LIMIT 1"))
        except Exception:
            db.session.rollback()
            try:
                db.session.execute(text("ALTER TABLE course_offerings ADD COLUMN priority INTEGER DEFAULT 1"))
                db.session.commit()
                print("Successfully added priority column to course_offerings!")
            except Exception as e:
                db.session.rollback()
                print(f"Error adding priority column: {e}")
        from app.models.models import Slot
        if not Slot.query.first():
            slots = [
                {"slot_code": "A1", "day": "Monday", "start_time": "08:00", "end_time": "08:50"},
                {"slot_code": "B1", "day": "Monday", "start_time": "09:00", "end_time": "09:50"},
                {"slot_code": "C1", "day": "Monday", "start_time": "10:00", "end_time": "10:50"},
                {"slot_code": "D1", "day": "Monday", "start_time": "11:00", "end_time": "11:50"},
                {"slot_code": "L1", "day": "Monday", "start_time": "14:00", "end_time": "15:40"},
                {"slot_code": "A2", "day": "Tuesday", "start_time": "08:00", "end_time": "08:50"},
                {"slot_code": "B2", "day": "Tuesday", "start_time": "09:00", "end_time": "09:50"},
                {"slot_code": "C2", "day": "Tuesday", "start_time": "10:00", "end_time": "10:50"},
                {"slot_code": "D2", "day": "Tuesday", "start_time": "11:00", "end_time": "11:50"},
                {"slot_code": "L2", "day": "Tuesday", "start_time": "14:00", "end_time": "15:40"},
            ]
            for s in slots:
                slot = Slot(**s)
                db.session.add(slot)
            db.session.commit()
            print("Default slots seeded successfully on startup!")

    @app.before_request
    def require_login():
        from flask import session, redirect, request
        # If the endpoint is None (e.g. 404), allow it to pass to the error handler or 404 page
        if request.endpoint is None:
            return
            
        allowed_endpoints = ['login_page', 'static', 'api.login', 'api.register']
        if request.endpoint not in allowed_endpoints and 'user_id' not in session:
            # Check if it's an API request, if so return 401 instead of redirect
            if request.path.startswith('/api/'):
                return jsonify({"error": "Unauthorized"}), 401
            return redirect('/login')

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
