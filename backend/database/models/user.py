"""
User model for authentication and user management
"""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from .base import BaseModel


class User(BaseModel):
    """User model for storing user information and authentication data"""
    
    __tablename__ = 'users'
    
    # Basic user information
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Email verification
    is_email_verified = Column(Boolean, default=False, nullable=False)
    email_verification_token = Column(String(255), nullable=True)
    email_verification_expires = Column(DateTime, nullable=True)
    
    # Password reset
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    sessions = relationship('Session', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, username, email, password):
        """Initialize user with hashed password"""
        self.username = username
        self.email = email
        self.set_password(password)
    
    def set_password(self, password):
        """Hash and set user password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches stored hash"""
        return check_password_hash(self.password_hash, password)
    
    def verify_email(self):
        """Mark email as verified"""
        self.is_email_verified = True
        self.email_verification_token = None
        self.save()
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        self.save()
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary, excluding sensitive data by default"""
        result = super().to_dict()
        
        # Remove sensitive fields unless explicitly requested
        if not include_sensitive:
            result.pop('password_hash', None)
            result.pop('email_verification_token', None)
        
        return result
    
    @classmethod
    def find_by_email(cls, email):
        """Find user by email address"""
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def find_by_username(cls, username):
        """Find user by username"""
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def find_by_verification_token(cls, token):
        """Find user by email verification token"""
        return cls.query.filter_by(email_verification_token=token).first()
    
    @classmethod
    def find_by_reset_token(cls, token):
        """Find user by password reset token"""
        return cls.query.filter_by(password_reset_token=token).first()
    
    def __repr__(self):
        return f'<User {self.username}>'