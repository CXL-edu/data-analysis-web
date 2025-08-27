"""
Decorators for authentication, authorization, and validation
"""
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError as MarshmallowValidationError
from .exceptions import ValidationError, AuthorizationError, NotFoundError
from database.repositories import UserRepository, SessionRepository


def validate_json(schema_class):
    """Decorator to validate JSON request data using marshmallow schema"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                raise ValidationError("Content-Type must be application/json")
            
            try:
                schema = schema_class()
                validated_data = schema.load(request.json)
                request.validated_data = validated_data
                return f(*args, **kwargs)
            except MarshmallowValidationError as e:
                raise ValidationError(str(e.messages))
        return decorated_function
    return decorator


def require_auth(f):
    """Decorator that requires valid JWT token"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        try:
            current_user_id = get_jwt_identity()
            print(f"JWT identity: {current_user_id}")
            
            if not current_user_id:
                print("No JWT identity found")
                raise AuthorizationError("Invalid token")
            
            # Convert string ID back to integer for database lookup
            try:
                user_id = int(current_user_id)
            except (ValueError, TypeError):
                print(f"Invalid user ID format: {current_user_id}")
                raise AuthorizationError("Invalid token format")
            
            # Get user from database and attach to request
            user_repo = UserRepository()
            user = user_repo.find_by_id(user_id)
            
            if not user:
                print(f"User with id {current_user_id} not found in database")
                raise AuthorizationError("User not found")
            
            if not user.is_active:
                print(f"User {user.username} is not active")
                raise AuthorizationError("Account is deactivated")
            
            print(f"Authentication successful for user: {user.username}")
            request.current_user = user
            return f(*args, **kwargs)
            
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            raise AuthorizationError(f"Authentication failed: {str(e)}")
    return decorated_function


def require_verified_email(f):
    """Decorator that requires verified email address"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(request, 'current_user'):
            raise AuthorizationError("Authentication required")
        
        if not request.current_user.is_email_verified:
            raise AuthorizationError("Email verification required")
        
        return f(*args, **kwargs)
    return decorated_function


def require_session_owner(f):
    """Decorator that ensures user owns the session"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(request, 'current_user'):
            raise AuthorizationError("Authentication required")
        
        session_id = kwargs.get('session_id') or request.view_args.get('session_id')
        if not session_id:
            raise ValidationError("Session ID is required")
        
        session_repo = SessionRepository()
        session = session_repo.find_by_id(session_id)
        
        if not session:
            raise NotFoundError("Session not found")
        
        if session.user_id != request.current_user.id:
            raise AuthorizationError("You don't have permission to access this session")
        
        request.current_session = session
        return f(*args, **kwargs)
    return decorated_function


def require_session_owner_by_uuid(f):
    """Decorator that ensures user owns the session (using UUID)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(request, 'current_user'):
            raise AuthorizationError("Authentication required")
        
        session_uuid = kwargs.get('session_uuid') or request.view_args.get('session_uuid')
        if not session_uuid:
            raise ValidationError("Session UUID is required")
        
        session_repo = SessionRepository()
        session = session_repo.find_by_uuid(session_uuid)
        
        if not session:
            raise NotFoundError("Session not found")
        
        if session.user_id != request.current_user.id:
            raise AuthorizationError("You don't have permission to access this session")
        
        request.current_session = session
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator for admin-only endpoints (if needed in future)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(request, 'current_user'):
            raise AuthorizationError("Authentication required")
        
        # For now, check if user is admin (could be a field in User model)
        # This is a placeholder for future admin functionality
        if not getattr(request.current_user, 'is_admin', False):
            raise AuthorizationError("Admin privileges required")
        
        return f(*args, **kwargs)
    return decorated_function


def rate_limit(requests_per_minute=60):
    """Simple rate limiting decorator (placeholder for future implementation)"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # TODO: Implement actual rate limiting logic
            # For now, just pass through
            return f(*args, **kwargs)
        return decorated_function
    return decorator