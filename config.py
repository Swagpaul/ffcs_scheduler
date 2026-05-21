import os
import sys

def get_db_uri():
    # If running inside PyInstaller bundle or Electron environment
    if getattr(sys, 'frozen', False) or os.getenv('ELECTRON_RUN') == '1':
        # Put database in the user's local application data folder
        app_data = os.environ.get('APPDATA') or os.environ.get('LOCALAPPDATA') or os.path.expanduser('~')
        app_dir = os.path.join(app_data, 'FFCS-Scheduler')
        os.makedirs(app_dir, exist_ok=True)
        db_path = os.path.join(app_dir, 'ffcs_scheduler.db')
        return f"sqlite:///{db_path}"
    
    # Otherwise, fall back to environment variable or standard relative SQLite path
    _db_url = os.getenv("DATABASE_URL")
    if _db_url:
        if _db_url.startswith("postgres://"):
            _db_url = _db_url.replace("postgres://", "postgresql://", 1)
        return _db_url
    
    # Default local dev SQLite database
    return "sqlite:///ffcs_scheduler.db"

def get_persistent_secret_key():
    key = os.getenv("SECRET_KEY")
    if key:
        return key
    
    # Otherwise, check in AppData directory for a persistent key file
    try:
        app_data = os.environ.get('APPDATA') or os.environ.get('LOCALAPPDATA') or os.path.expanduser('~')
        app_dir = os.path.join(app_data, 'FFCS-Scheduler')
        os.makedirs(app_dir, exist_ok=True)
        key_file = os.path.join(app_dir, 'secret_key.txt')
        
        if os.path.exists(key_file):
            with open(key_file, 'r') as f:
                return f.read().strip()
        
        # Generate new one
        import secrets
        new_key = secrets.token_hex(24)
        with open(key_file, 'w') as f:
            f.write(new_key)
        return new_key
    except Exception:
        return "dev-key-123"

class BaseConfig:
    SECRET_KEY = get_persistent_secret_key()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = get_db_uri()
    DEBUG = True

class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = get_db_uri()
    DEBUG = False

config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}
