import os
import sys
import logging
from flask import Flask
from app.config import Config
from app.database.db import db

def setup_logging(app_config):
    """Configures structured logs splitting stdout stream logs by severity level."""
    # Root logger format
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    
    # stdout info handler
    info_handler = logging.StreamHandler(sys.stdout)
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)
    
    # stderr error handler
    error_handler = logging.StreamHandler(sys.stderr)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(app_config.LOG_LEVEL)
    
    # Remove default Flask handlers if any
    for h in list(root_logger.handlers):
        root_logger.removeHandler(h)
        
    root_logger.addHandler(info_handler)
    root_logger.addHandler(error_handler)

def create_app():
    """Application factory initializing logger, databases, and registering Blueprints."""
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)
    
    # Configure logs
    setup_logging(Config)
    
    # Bind database SQLAlchemy
    db.init_app(app)
    
    # Register blueprints
    from app.routes.web import web_bp
    from app.routes.webhook import webhook_bp
    
    app.register_blueprint(web_bp)
    app.register_blueprint(webhook_bp)
    
    # Automatic DB migration / creation
    with app.app_context():
        db.create_all()
        
        # Populate slots dynamically
        from app.services import slot_service
        slot_service.generate_slots_for_next_30_days()
        
    return app
