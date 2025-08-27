"""
User repository for user-specific database operations
"""
from .base_repository import BaseRepository
from database.models import User


class UserRepository(BaseRepository):
    """Repository for User model operations"""
    
    def __init__(self):
        super().__init__(User)
    
    def create_user(self, username, email, password):
        """Create a new user with hashed password"""
        user = User(username=username, email=email, password=password)
        user.save()
        return user
    
    def find_by_email(self, email):
        """Find user by email address"""
        return self.model.find_by_email(email)
    
    def find_by_username(self, username):
        """Find user by username"""
        return self.model.find_by_username(username)
    
    def find_by_verification_token(self, token):
        """Find user by email verification token"""
        return self.model.find_by_verification_token(token)
    
    def find_by_reset_token(self, token):
        """Find user by password reset token"""
        return self.model.find_by_reset_token(token)
    
    def update_verification_token(self, user_id, token):
        """Update user's email verification token"""
        return self.update(user_id, email_verification_token=token)
    
    def verify_user_email(self, user_id):
        """Mark user's email as verified"""
        user = self.find_by_id(user_id)
        if user:
            user.verify_email()
            return user
        return None
    
    def update_last_login(self, user_id):
        """Update user's last login timestamp"""
        user = self.find_by_id(user_id)
        if user:
            user.update_last_login()
            return user
        return None
    
    def deactivate_user(self, user_id):
        """Deactivate user account"""
        return self.update(user_id, is_active=False)
    
    def activate_user(self, user_id):
        """Activate user account"""
        return self.update(user_id, is_active=True)
    
    def change_password(self, user_id, new_password):
        """Change user password"""
        user = self.find_by_id(user_id)
        if user:
            user.set_password(new_password)
            user.save()
            return user
        return None
    
    def is_email_taken(self, email, exclude_user_id=None):
        """Check if email is already taken by another user"""
        query = self.model.query.filter_by(email=email)
        if exclude_user_id:
            query = query.filter(self.model.id != exclude_user_id)
        return query.first() is not None
    
    def is_username_taken(self, username, exclude_user_id=None):
        """Check if username is already taken by another user"""
        query = self.model.query.filter_by(username=username)
        if exclude_user_id:
            query = query.filter(self.model.id != exclude_user_id)
        return query.first() is not None
    
    def find_active_users(self):
        """Find all active users"""
        return self.find_all(is_active=True)
    
    def find_verified_users(self):
        """Find all users with verified emails"""
        return self.find_all(is_email_verified=True)
    
    def update_user_profile(self, user_id, profile_data):
        """Update user profile data"""
        user = self.find_by_id(user_id)
        if not user:
            return None
        
        for key, value in profile_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        user.save()
        return user
    
    def update_user(self, user):
        """Update and save user object"""
        user.save()
        return user
    
    def get_user_stats(self, user_id):
        """Get user statistics"""
        user = self.find_by_id(user_id)
        if not user:
            return None
        
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_verified': user.is_email_verified,
            'is_active': user.is_active,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'created_at': user.created_at.isoformat(),
            'session_count': user.sessions.count()
        }