"""
Authentication API schemas
"""
from marshmallow import Schema, fields, validate, validates, ValidationError
from database.repositories import UserRepository


class RegisterSchema(Schema):
    """Schema for user registration"""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6, max=128))
    confirm_password = fields.Str(required=True)
    
    @validates('username')
    def validate_username(self, value, **kwargs):
        user_repo = UserRepository()
        if user_repo.is_username_taken(value):
            raise ValidationError('Username is already taken')
    
    @validates('email')
    def validate_email(self, value, **kwargs):
        user_repo = UserRepository()
        if user_repo.is_email_taken(value):
            raise ValidationError('Email is already registered')
    
    def validate(self, data, **kwargs):
        errors = super().validate(data, **kwargs)
        if data.get('password') != data.get('confirm_password'):
            errors['confirm_password'] = ['Passwords do not match']
        return errors


class SendVerificationSchema(Schema):
    """Schema for sending verification code"""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6, max=128))
    confirm_password = fields.Str(required=True)
    
    def validate(self, data, **kwargs):
        errors = super().validate(data, **kwargs)
        if data.get('password') != data.get('confirm_password'):
            errors['confirm_password'] = ['Passwords do not match']
        return errors


class LoginSchema(Schema):
    """Schema for user login"""
    email = fields.Email(required=True)
    password = fields.Str(required=True)


class RefreshTokenSchema(Schema):
    """Schema for token refresh"""
    refresh_token = fields.Str(required=True)


class ForgotPasswordSchema(Schema):
    """Schema for forgot password request"""
    email = fields.Email(required=True)


class ResetPasswordSchema(Schema):
    """Schema for password reset"""
    token = fields.Str(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6, max=128))
    confirm_password = fields.Str(required=True)
    
    def validate(self, data, **kwargs):
        errors = super().validate(data, **kwargs)
        if data.get('password') != data.get('confirm_password'):
            errors['confirm_password'] = ['Passwords do not match']
        return errors


class ChangePasswordSchema(Schema):
    """Schema for changing password"""
    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=6, max=128))
    confirm_password = fields.Str(required=True)
    
    def validate(self, data, **kwargs):
        errors = super().validate(data, **kwargs)
        if data.get('new_password') != data.get('confirm_password'):
            errors['confirm_password'] = ['Passwords do not match']
        return errors


class UpdateProfileSchema(Schema):
    """Schema for updating user profile"""
    username = fields.Str(validate=validate.Length(min=3, max=50))
    email = fields.Email()
    
    @validates('username')
    def validate_username(self, value, **kwargs):
        # Get current user ID from request context if needed
        # This would need to be implemented based on your request context
        user_repo = UserRepository()
        if user_repo.is_username_taken(value):
            raise ValidationError('Username is already taken')
    
    @validates('email')
    def validate_email(self, value, **kwargs):
        # Get current user ID from request context if needed
        user_repo = UserRepository()
        if user_repo.is_email_taken(value):
            raise ValidationError('Email is already registered')