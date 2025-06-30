import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_mail import Mail

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
mail = Mail()

def create_app():
    # Create the app
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET", "hiddekel-dev-secret-key-2024")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Configure the database
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///hiddekel.db")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Mail configuration
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', '587'))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'hiddekel.investment@gmail.com')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'your-app-password')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'hiddekel.investment@gmail.com')
    
    # Upload configuration
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    
    # Create upload directory
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    with app.app_context():
        # Import models to ensure tables are created
        import models
        db.create_all()
        
        # Import and register routes
        from routes import main_bp
        from admin_routes import admin_bp
        
        app.register_blueprint(main_bp)
        app.register_blueprint(admin_bp, url_prefix='/admin')
        
        # Add context processor for site settings
        @app.context_processor
        def inject_site_settings():
            from models import SiteSetting
            settings = {}
            for setting in SiteSetting.query.all():
                settings[setting.key] = setting.value
            return {'site_settings': settings}
        
        # Seed initial data if needed
        from seed_data import seed_initial_data
        seed_initial_data()
    
    return app

# Create the app instance
app = create_app()
