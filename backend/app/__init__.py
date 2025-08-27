"""
AI Data Assistant Backend Application
"""

import os
from flask import Flask
from flask_restx import Api
from .extensions import init_extensions
from .config import config


def create_app(config_name='development'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    init_extensions(app)
    
    # Create upload directory
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Create API instance with Flask-RESTX
    api = Api(
        app,
        version='1.0',
        title='AI Data Assistant API',
        description='RESTful API for AI-powered data analysis',
        doc='/api/docs/',
        prefix='/api/v1'
    )
    
    # Register API namespaces
    from app.api.v1 import register_namespaces
    register_namespaces(api)
    
    # Compatibility layer removed - using full authentication system
    
    # Register error handlers
    from app.utils.exceptions import register_error_handlers
    register_error_handlers(app)
    
    return app