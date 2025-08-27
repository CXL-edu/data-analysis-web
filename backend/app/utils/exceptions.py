"""
Custom exceptions and error handlers
"""
from flask import jsonify
from flask_restx import Api
from werkzeug.exceptions import HTTPException
from flask_jwt_extended.exceptions import JWTExtendedException


class ValidationError(Exception):
    """Custom validation error"""
    def __init__(self, message, field=None):
        super().__init__(message)
        self.message = message
        self.field = field


class AuthenticationError(Exception):
    """Custom authentication error"""
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class AuthorizationError(Exception):
    """Custom authorization error"""
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class NotFoundError(Exception):
    """Custom not found error"""
    def __init__(self, message):
        super().__init__(message)
        self.message = message


def register_error_handlers(app):
    """Register error handlers for the Flask app"""
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        return jsonify({
            'error': 'Validation Error',
            'message': e.message,
            'field': e.field
        }), 400
    
    @app.errorhandler(AuthenticationError)
    def handle_authentication_error(e):
        return jsonify({
            'error': 'Authentication Error',
            'message': e.message
        }), 401
    
    @app.errorhandler(AuthorizationError)
    def handle_authorization_error(e):
        return jsonify({
            'error': 'Authorization Error',
            'message': e.message
        }), 403
    
    @app.errorhandler(NotFoundError)
    def handle_not_found_error(e):
        return jsonify({
            'error': 'Not Found',
            'message': e.message
        }), 404
    
    @app.errorhandler(JWTExtendedException)
    def handle_jwt_exceptions(e):
        return jsonify({
            'error': 'JWT Error',
            'message': str(e)
        }), 401
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return jsonify({
            'error': e.name,
            'message': e.description
        }), e.code
    
    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        app.logger.error(f"Unhandled exception: {str(e)}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500