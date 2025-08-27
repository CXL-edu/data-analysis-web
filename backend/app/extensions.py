"""
Flask extensions initialization
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_cors import CORS

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()
cors = CORS()

def init_extensions(app):
    """Initialize Flask extensions with app instance"""
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    
    # Configure CORS with specific settings
    cors.init_app(app, 
                  origins=app.config.get('CORS_ORIGINS', ['http://localhost:3000']),
                  supports_credentials=True,
                  allow_headers=[
                      'Content-Type', 
                      'Authorization', 
                      'Access-Control-Allow-Credentials', 
                      'Access-Control-Allow-Origin',
                      'X-Requested-With',
                      'Accept',
                      'Origin'
                  ],
                  expose_headers=['Content-Type', 'Authorization'],
                  methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD'],
                  send_wildcard=False,
                  vary_header=True)
    
    # Import models to ensure they are registered with SQLAlchemy
    from database.models import User, Session, UploadedFile, ChatMessage, AnalysisResult
    
    return app