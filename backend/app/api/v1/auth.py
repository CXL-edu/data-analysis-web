"""
Authentication API endpoints
"""
from flask import request, jsonify
from flask_restx import Namespace, Resource
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from app.utils.decorators import validate_json, require_auth
from app.api.schemas.auth_schemas import (
    RegisterSchema, SendVerificationSchema, LoginSchema, RefreshTokenSchema, 
    ForgotPasswordSchema, ResetPasswordSchema, 
    ChangePasswordSchema, UpdateProfileSchema
)
from app.services.auth_service import AuthService
from app.utils.exceptions import ValidationError, AuthorizationError, NotFoundError

auth_ns = Namespace('auth', description='Authentication operations')

@auth_ns.route('/register')
class RegisterResource(Resource):
    def options(self):
        """Handle preflight request for registration"""
        from flask import make_response
        response = make_response({})
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

    @validate_json(SendVerificationSchema)
    def post(self):
        """Send verification code for registration"""
        try:
            print(f"Registration request data: {request.validated_data}")
            auth_service = AuthService()
            result = auth_service.send_registration_code(request.validated_data)
            print(f"Verification code sent to: {request.validated_data['email']}")
            return {
                'message': '验证码已发送到您的邮箱，请查收并输入验证码完成注册',
                'email': request.validated_data['email'],
                'next_step': 'verify_code'
            }, 200
        except ValidationError as e:
            print(f"Validation error during registration: {str(e)}")
            return {'error': str(e)}, 400
        except Exception as e:
            print(f"Unexpected error during registration: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'error': f'Registration failed: {str(e)}'}, 500

@auth_ns.route('/verify-registration')
class VerifyRegistrationResource(Resource):
    def post(self):
        """Verify registration code and create user"""
        try:
            data = request.get_json()
            if not data or 'email' not in data or 'code' not in data:
                return {'error': '缺少邮箱或验证码'}, 400
                
            auth_service = AuthService()
            user = auth_service.verify_registration_code(data)
            print(f"User registered successfully: {user.username}, {user.email}")
            
            return {
                'message': '注册成功！您现在可以登录了。',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_email_verified': user.is_email_verified
                }
            }, 201
        except ValidationError as e:
            print(f"Validation error during code verification: {str(e)}")
            return {'error': str(e)}, 400
        except Exception as e:
            print(f"Unexpected error during code verification: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'error': f'验证失败: {str(e)}'}, 500

@auth_ns.route('/resend-verification')
class ResendVerificationCodeResource(Resource):
    def post(self):
        """Resend verification code"""
        try:
            data = request.get_json()
            if not data or 'email' not in data:
                return {'error': '缺少邮箱地址'}, 400
                
            auth_service = AuthService()
            result = auth_service.resend_verification_code(data['email'])
            
            return {
                'message': '验证码已重新发送，请查收邮件'
            }, 200
        except ValidationError as e:
            print(f"Validation error during resend: {str(e)}")
            return {'error': str(e)}, 400
        except Exception as e:
            print(f"Unexpected error during resend: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'error': f'重新发送失败: {str(e)}'}, 500

@auth_ns.route('/login')
class LoginResource(Resource):
    def options(self):
        """Handle preflight request for login"""
        from flask import make_response
        response = make_response({})
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

    @validate_json(LoginSchema)
    def post(self):
        """Login user and return JWT tokens"""
        try:
            auth_service = AuthService()
            result = auth_service.login_user(request.validated_data)
            
            return {
                'message': 'Login successful',
                'access_token': result['access_token'],
                'refresh_token': result['refresh_token'],
                'user': {
                    'id': result['user'].id,
                    'username': result['user'].username,
                    'email': result['user'].email,
                    'is_email_verified': result['user'].is_email_verified
                }
            }, 200
        except AuthorizationError as e:
            return {'error': str(e)}, 401
        except Exception as e:
            return {'error': 'Login failed'}, 500

@auth_ns.route('/refresh')
class RefreshTokenResource(Resource):
    @validate_json(RefreshTokenSchema)
    def post(self):
        """Refresh access token using refresh token"""
        try:
            auth_service = AuthService()
            new_token = auth_service.refresh_token(request.validated_data['refresh_token'])
            
            return {
                'access_token': new_token
            }, 200
        except AuthorizationError as e:
            return {'error': str(e)}, 401
        except Exception as e:
            return {'error': 'Token refresh failed'}, 500

@auth_ns.route('/logout')
class LogoutResource(Resource):
    @require_auth
    def post(self):
        """Logout user (invalidate tokens)"""
        # TODO: Implement token blacklisting if needed
        return {'message': 'Logged out successfully'}, 200

@auth_ns.route('/profile')
class ProfileResource(Resource):
    @require_auth
    def get(self):
        """Get current user profile"""
        user = request.current_user
        return {
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_email_verified': user.is_email_verified,
                'created_at': user.created_at.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
        }, 200
    
    @require_auth
    @validate_json(UpdateProfileSchema)
    def put(self):
        """Update user profile"""
        try:
            auth_service = AuthService()
            user = auth_service.update_profile(request.current_user.id, request.validated_data)
            
            return {
                'message': 'Profile updated successfully',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_email_verified': user.is_email_verified
                }
            }, 200
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': 'Profile update failed'}, 500

@auth_ns.route('/verify-email/<token>')
class EmailVerificationResource(Resource):
    def get(self, token):
        """Verify email address"""
        try:
            auth_service = AuthService()
            user = auth_service.verify_email(token)
            
            return {
                'message': 'Email verified successfully',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_email_verified': user.is_email_verified
                }
            }, 200
        except AuthorizationError as e:
            return {'error': str(e)}, 401
        except NotFoundError as e:
            return {'error': str(e)}, 404
        except Exception as e:
            return {'error': 'Email verification failed'}, 500

@auth_ns.route('/resend-verification')
class ResendVerificationResource(Resource):
    @require_auth
    def post(self):
        """Resend email verification"""
        try:
            if request.current_user.is_email_verified:
                return {'message': 'Email is already verified'}, 200
            
            auth_service = AuthService()
            auth_service.send_verification_email(request.current_user)
            
            return {'message': 'Verification email sent'}, 200
        except Exception as e:
            return {'error': 'Failed to send verification email'}, 500

@auth_ns.route('/forgot-password')
class ForgotPasswordResource(Resource):
    @validate_json(ForgotPasswordSchema)
    def post(self):
        """Request password reset"""
        try:
            auth_service = AuthService()
            auth_service.request_password_reset(request.validated_data['email'])
            
            return {
                'message': 'If your email is registered, you will receive password reset instructions.'
            }, 200
        except Exception as e:
            return {'error': 'Password reset request failed'}, 500

@auth_ns.route('/reset-password')
class ResetPasswordResource(Resource):
    @validate_json(ResetPasswordSchema)
    def post(self):
        """Reset password using token"""
        try:
            auth_service = AuthService()
            auth_service.reset_password(request.validated_data)
            
            return {'message': 'Password reset successfully'}, 200
        except AuthorizationError as e:
            return {'error': str(e)}, 401
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': 'Password reset failed'}, 500

@auth_ns.route('/change-password')
class ChangePasswordResource(Resource):
    @require_auth
    @validate_json(ChangePasswordSchema)
    def post(self):
        """Change password for authenticated user"""
        try:
            auth_service = AuthService()
            auth_service.change_password(request.current_user.id, request.validated_data)
            
            return {'message': 'Password changed successfully'}, 200
        except AuthorizationError as e:
            return {'error': str(e)}, 401
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': 'Password change failed'}, 500