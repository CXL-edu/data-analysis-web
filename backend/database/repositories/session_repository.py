"""
Session repository for session-specific database operations
"""
from .base_repository import BaseRepository
from database.models import Session
from database import db


class SessionRepository(BaseRepository):
    """Repository for Session model operations"""
    
    def __init__(self):
        super().__init__(Session)
    
    def create_session(self, user_id, title=None):
        """Create a new session for a user"""
        session = Session(user_id=user_id, title=title)
        session.save()
        return session
    
    def find_by_uuid(self, session_uuid):
        """Find session by UUID"""
        return self.model.find_by_uuid(session_uuid)
    
    def find_by_user(self, user_id, active_only=True):
        """Find all sessions for a user"""
        return self.model.find_by_user(user_id, active_only)
    
    def find_by_user_id(self, user_id):
        """Find all sessions for a user (compatibility method)"""
        return self.find_by_user(user_id, active_only=False)
    
    def find_recent_by_user(self, user_id, limit=10):
        """Find recent sessions for a user"""
        return self.model.find_recent_by_user(user_id, limit)
    
    def update_title(self, session_id, title):
        """Update session title"""
        session = self.find_by_id(session_id)
        if session:
            session.update_title(title)
            return session
        return None
    
    def deactivate_session(self, session_id):
        """Deactivate session instead of deleting"""
        session = self.find_by_id(session_id)
        if session:
            session.deactivate()
            return session
        return None
    
    def reactivate_session(self, session_id):
        """Reactivate a deactivated session"""
        return self.update(session_id, is_active=True)
    
    def delete_session(self, session_id, user_id):
        """Delete session only if it belongs to the user"""
        session = self.find_by_id(session_id)
        if session and session.user_id == user_id:
            session.delete()
            return True
        return False
    
    def get_user_session_stats(self, user_id):
        """Get session statistics for a user"""
        total_sessions = self.count(user_id=user_id)
        active_sessions = self.count(user_id=user_id, is_active=True)
        
        return {
            'total_sessions': total_sessions,
            'active_sessions': active_sessions,
            'inactive_sessions': total_sessions - active_sessions
        }
    
    def find_sessions_with_files(self, user_id):
        """Find user sessions that have uploaded files"""
        return db.session.query(Session)\
                         .filter_by(user_id=user_id, is_active=True)\
                         .join(Session.uploaded_files)\
                         .distinct()\
                         .all()
    
    def find_sessions_with_recent_activity(self, user_id, days=7):
        """Find user sessions with recent activity"""
        from datetime import datetime, timedelta
        since_date = datetime.utcnow() - timedelta(days=days)
        
        return self.model.query\
                        .filter_by(user_id=user_id, is_active=True)\
                        .filter(self.model.updated_at >= since_date)\
                        .order_by(self.model.updated_at.desc())\
                        .all()
    
    def get_session_details(self, session_id, user_id=None):
        """Get detailed session information"""
        session = self.find_by_id(session_id)
        if not session:
            return None
        
        # Check user permission if provided
        if user_id and session.user_id != user_id:
            return None
        
        return {
            'session': session.to_dict(include_stats=True),
            'message_count': session.get_message_count(),
            'file_count': session.get_file_count(),
            'latest_message': session.get_latest_message().to_dict() if session.get_latest_message() else None,
            'files': [file.to_dict() for file in session.uploaded_files],
            'recent_messages': [msg.to_dict() for msg in session.chat_messages.limit(5).all()]
        }
    
    def search_user_sessions(self, user_id, query):
        """Search sessions by title for a user"""
        return self.model.query\
                        .filter_by(user_id=user_id, is_active=True)\
                        .filter(self.model.title.contains(query))\
                        .order_by(self.model.updated_at.desc())\
                        .all()
    
    def bulk_deactivate_old_sessions(self, user_id, keep_recent=50):
        """Deactivate old sessions, keeping only recent ones"""
        recent_sessions = self.find_recent_by_user(user_id, keep_recent)
        recent_ids = [s.id for s in recent_sessions]
        
        old_sessions = self.model.query\
                                .filter_by(user_id=user_id, is_active=True)\
                                .filter(~self.model.id.in_(recent_ids))\
                                .all()
        
        count = 0
        for session in old_sessions:
            session.deactivate()
            count += 1
        
        return count