"""
Configuration settings for the AI Data Assistant Backend
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ai-data-assistant-secret-key-2024'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # JWT settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)  # Extended for testing
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_ALGORITHM = 'HS256'
    
    # Mail settings（鉴权信息仅从环境变量读取，不写死在代码中）
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or os.environ.get('SMTP_HOST') or 'localhost'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or os.environ.get('SMTP_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or os.environ.get('SMTP_FROM_EMAIL')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or os.environ.get('SMTP_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or os.environ.get('SMTP_FROM_EMAIL') or 'noreply@fumadocs.com'
    # 阿里云等 SMTP 专用变量（与 MAIL_* 二选一即可）
    SMTP_HOST = os.environ.get('SMTP_HOST')
    SMTP_PORT = os.environ.get('SMTP_PORT')
    SMTP_FROM_EMAIL = os.environ.get('SMTP_FROM_EMAIL')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'storage', 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'ods'}
    
    # CORS settings
    CORS_ORIGINS = [
        'http://localhost:3000', 
        'http://127.0.0.1:3000',
        'http://localhost:3001',
        'http://127.0.0.1:3001'
    ]
    
    # Frontend settings
    FRONTEND_URL = os.environ.get('FRONTEND_URL') or 'http://127.0.0.1:3000'
    
    # Chart settings
    CHART_DPI = 150
    CHART_FORMAT = 'png'
    CHART_FIGSIZE = (10, 6)
    
    # Analysis settings
    MAX_PREVIEW_ROWS = 5
    MAX_CORRELATION_FEATURES = 20
    
    # Security settings
    BCRYPT_LOG_ROUNDS = 13
    WTF_CSRF_ENABLED = False
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    # Use SQLite by default for development if no DATABASE_URL is provided
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'app.db')
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://localhost/fumadocs_prod'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    
class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/fumadocs_test'
    UPLOAD_FOLDER = '/tmp/ai_data_assistant_test'
    WTF_CSRF_ENABLED = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=1)

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}