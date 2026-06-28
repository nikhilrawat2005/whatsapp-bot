import os
import logging
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask Environment Configurations
    SECRET_KEY = os.environ.get('SECRET_KEY', 'abc-hospital-session-secret-key-9988')
    SESSION_SECRET = os.environ.get('SESSION_SECRET', SECRET_KEY)
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
    PORT = int(os.environ.get('PORT', 5000))
    
    # Database configuration logic - Dynamic fallback to SQLite
    raw_db_url = os.environ.get('DATABASE_URL')
    if raw_db_url:
        # Render PostgreSQL URL fixes (replace postgres:// with postgresql://)
        if raw_db_url.startswith("postgres://"):
            raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = raw_db_url
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///hospital.db'
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Meta WhatsApp API Credentials
    WHATSAPP_TOKEN = os.environ.get('WHATSAPP_TOKEN', '')
    WHATSAPP_PHONE_NUMBER_ID = os.environ.get('WHATSAPP_PHONE_NUMBER_ID', '')
    WHATSAPP_VERIFY_TOKEN = os.environ.get('WHATSAPP_VERIFY_TOKEN', 'abc_hospital_verify_token_123')
    
    # Logger Configurations
    LOG_LEVEL = logging.DEBUG if FLASK_ENV == 'development' else logging.INFO
