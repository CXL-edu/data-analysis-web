"""
Authentication service for user management
"""
import secrets
from datetime import datetime, timedelta, timezone
from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, mail
from database.repositories.user_repository import UserRepository
from app.utils.exceptions import ValidationError, AuthorizationError, NotFoundError
from app.services.email_service import email_service


class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()
    
    def send_registration_code(self, user_data):
        """Send verification code for registration"""
        # Check if username or email already exists
        if self.user_repo.is_username_taken(user_data['username']):
            raise ValidationError('用户名已被使用')
        
        if self.user_repo.is_email_taken(user_data['email']):
            raise ValidationError('邮箱已被注册')
        
        # 发送验证码邮件（EmailService将存储验证码和用户数据）
        email = user_data['email']
        success, code_or_error = email_service.send_registration_email(
            email, 
            user_data['username'], 
            user_data
        )
        
        if not success:
            raise ValidationError(f'发送验证码失败: {code_or_error}')
        
        return {'success': True, 'code': code_or_error if current_app.config.get('DEBUG') else None}
    
    def verify_registration_code(self, verification_data):
        """Verify code and create user"""
        email = verification_data['email']
        code = verification_data['code']
        
        # 验证验证码并获取用户数据
        is_valid, message, user_data = email_service.verify_registration_code(email, code)
        if not is_valid:
            raise ValidationError(message)
        
        # 再次检查用户名和邮箱是否被占用（防止并发问题）
        if self.user_repo.is_username_taken(user_data['username']):
            raise ValidationError('用户名已被使用')
        
        if self.user_repo.is_email_taken(user_data['email']):
            raise ValidationError('邮箱已被注册')
        
        # 创建用户
        user = self.user_repo.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password']
        )
        
        # 直接设为已验证（因为已通过邮箱验证码验证）
        user.is_email_verified = True
        self.user_repo.update_user(user)
        
        # 发送欢迎邮件
        try:
            email_service.send_welcome_email(user.email, user.username)
        except:
            pass  # 欢迎邮件失败不影响注册
        
        return user
    
    def resend_verification_code(self, email):
        """Resend verification code"""
        # 使用EmailService重新发送验证码
        success, error_message = email_service.resend_registration_code(email)
        if not success:
            raise ValidationError(error_message)
        
        return {'success': True}
    
    def login_user(self, login_data):
        """Authenticate user and return tokens"""
        user = self.user_repo.find_by_email(login_data['email'])
        
        if not user or not user.check_password(login_data['password']):
            raise AuthorizationError('Invalid email or password')
        
        if not user.is_active:
            raise AuthorizationError('Account is deactivated')
        
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        self.user_repo.update_user(user)
        
        # Create tokens
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return {
            'user': user,
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    
    def refresh_token(self, refresh_token):
        """Refresh access token"""
        try:
            decoded_token = decode_token(refresh_token)
            user_id_str = decoded_token['sub']
            user_id = int(user_id_str)  # Convert string back to int
            
            user = self.user_repo.find_by_id(user_id)
            if not user or not user.is_active:
                raise AuthorizationError('Invalid token')
            
            new_access_token = create_access_token(identity=str(user_id))
            return new_access_token
            
        except Exception:
            raise AuthorizationError('Invalid refresh token')
    
    def update_profile(self, user_id, profile_data):
        """Update user profile"""
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise NotFoundError('User not found')
        
        # Check username availability if changed
        if 'username' in profile_data and profile_data['username'] != user.username:
            if self.user_repo.is_username_taken(profile_data['username']):
                raise ValidationError('Username is already taken')
        
        # Check email availability if changed
        if 'email' in profile_data and profile_data['email'] != user.email:
            if self.user_repo.is_email_taken(profile_data['email']):
                raise ValidationError('Email is already registered')
            # If email changed, mark as unverified and send new verification
            user.is_email_verified = False
            self.send_verification_email(user)
        
        # Update user
        return self.user_repo.update_user_profile(user_id, profile_data)
    
    def send_verification_email(self, user):
        """Send email verification"""
        try:
            # Generate verification token
            token = secrets.token_urlsafe(32)
            expiry = datetime.now(timezone.utc) + timedelta(hours=24)
            
            user.email_verification_token = token
            user.email_verification_expires = expiry
            self.user_repo.update_user(user)
            
            # Send email
            verification_url = f"{current_app.config['FRONTEND_URL']}/verify-email/{token}"
            
            msg = Message(
                subject='Verify Your Email Address',
                sender=current_app.config['MAIL_DEFAULT_SENDER'],
                recipients=[user.email]
            )
            
            msg.body = f"""
            Hello {user.username},
            
            Please click the link below to verify your email address:
            {verification_url}
            
            This link will expire in 24 hours.
            
            If you didn't create this account, please ignore this email.
            
            Best regards,
            AI Data Assistant Team
            """
            
            # For development, just print the verification link instead of sending email
            if current_app.config.get('DEBUG', False):
                print(f"📧 Email verification link for {user.email}:")
                print(f"   {verification_url}")
                print("   (Email sending disabled in development mode)")
            else:
                mail.send(msg)
                print(f"📧 Verification email sent to {user.email}")
                
        except Exception as e:
            print(f"Warning: Failed to send verification email: {str(e)}")
            # Don't fail registration if email sending fails
            pass
    
    def verify_email(self, token):
        """Verify email address using token"""
        user = self.user_repo.find_by_verification_token(token)
        
        if not user:
            raise NotFoundError('Invalid verification token')
        
        if user.email_verification_expires < datetime.now(timezone.utc):
            raise AuthorizationError('Verification token has expired')
        
        # Mark email as verified
        user.is_email_verified = True
        user.email_verification_token = None
        user.email_verification_expires = None
        
        return self.user_repo.update_user(user)
    
    def request_password_reset(self, email):
        """Request password reset"""
        user = self.user_repo.find_by_email(email)
        
        if user:  # Always send success message for security
            # Generate reset token
            token = secrets.token_urlsafe(32)
            expiry = datetime.now(timezone.utc) + timedelta(hours=1)
            
            user.password_reset_token = token
            user.password_reset_expires = expiry
            self.user_repo.update_user(user)
            
            # Send reset email
            reset_url = f"{current_app.config['FRONTEND_URL']}/reset-password/{token}"
            
            msg = Message(
                subject='Password Reset Request',
                sender=current_app.config['MAIL_DEFAULT_SENDER'],
                recipients=[user.email]
            )
            
            msg.body = f"""
            Hello {user.username},
            
            You requested a password reset. Click the link below to reset your password:
            {reset_url}
            
            This link will expire in 1 hour.
            
            If you didn't request this reset, please ignore this email.
            
            Best regards,
            AI Data Assistant Team
            """
            
            mail.send(msg)
    
    def reset_password(self, reset_data):
        """Reset password using token"""
        user = self.user_repo.find_by_reset_token(reset_data['token'])
        
        if not user:
            raise AuthorizationError('Invalid reset token')
        
        if user.password_reset_expires < datetime.now(timezone.utc):
            raise AuthorizationError('Reset token has expired')
        
        # Update password
        user.password = generate_password_hash(reset_data['password'])
        user.password_reset_token = None
        user.password_reset_expires = None
        
        return self.user_repo.update_user(user)
    
    def change_password(self, user_id, password_data):
        """Change password for authenticated user"""
        user = self.user_repo.find_by_id(user_id)
        
        if not user:
            raise NotFoundError('User not found')
        
        if not user.check_password(password_data['current_password']):
            raise AuthorizationError('Current password is incorrect')
        
        # Update password
        user.password = generate_password_hash(password_data['new_password'])
        return self.user_repo.update_user(user)