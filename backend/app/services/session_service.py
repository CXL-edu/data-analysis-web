"""
Session management service
"""
from datetime import datetime
from app.extensions import db
from database.repositories.session_repository import SessionRepository
from database.repositories.message_repository import MessageRepository
from database.repositories.analysis_repository import AnalysisRepository
from database.models import UploadedFile
from app.utils.exceptions import NotFoundError, ValidationError
import os


class SessionService:
    def __init__(self):
        self.session_repo = SessionRepository()
        self.message_repo = MessageRepository()
        self.analysis_repo = AnalysisRepository()
    
    def create_session(self, user_id, title=None):
        """Create a new session for user"""
        if not title:
            title = f"Session {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        
        return self.session_repo.create_session(user_id, title)
    
    def get_user_sessions(self, user_id):
        """Get all sessions for a user"""
        return self.session_repo.find_by_user_id(user_id)
    
    def get_session_by_uuid(self, session_uuid):
        """Get session by UUID"""
        session = self.session_repo.find_by_uuid(session_uuid)
        if not session:
            raise NotFoundError('Session not found')
        return session
    
    def update_session(self, session_id, update_data):
        """Update session details"""
        session = self.session_repo.find_by_id(session_id)
        if not session:
            raise NotFoundError('Session not found')
        
        return self.session_repo.update_session(session_id, update_data)
    
    def delete_session(self, session_id):
        """Delete session and all associated data"""
        session = self.session_repo.find_by_id(session_id)
        if not session:
            raise NotFoundError('Session not found')
        
        # Delete all associated files from disk
        files = UploadedFile.find_by_session(session_id)
        for file in files:
            if os.path.exists(file.file_path):
                try:
                    os.remove(file.file_path)
                except OSError:
                    pass  # File might be in use or already deleted
        
        # Delete from database (cascade will handle related records)
        return self.session_repo.delete_session(session_id)
    
    def clear_session_data(self, session_id):
        """Clear all messages, files, and analysis results from session (keep session)"""
        session = self.session_repo.find_by_id(session_id)
        if not session:
            raise NotFoundError('Session not found')
        
        # Delete all files from disk
        files = UploadedFile.find_by_session(session_id)
        for file in files:
            if os.path.exists(file.file_path):
                try:
                    os.remove(file.file_path)
                except OSError:
                    pass
        
        # Clear all data
        self.message_repo.delete_by_session_id(session_id)
        # Delete files from database
        for file in files:
            file.delete()
        self.analysis_repo.delete_by_session_id(session_id)
        
        # Update session timestamp
        session.updated_at = datetime.utcnow()
        return self.session_repo.update_session(session_id, {'updated_at': session.updated_at})
    
    def get_session_stats(self, session_id):
        """Get session statistics"""
        session = self.session_repo.find_by_id(session_id)
        if not session:
            raise NotFoundError('Session not found')
        
        messages = self.message_repo.find_by_session_id(session_id)
        files = UploadedFile.find_by_session(session_id)
        analyses = self.analysis_repo.find_by_session_id(session_id)
        
        return {
            'session_id': session_id,
            'message_count': len(messages),
            'file_count': len(files),
            'analysis_count': len(analyses),
            'created_at': session.created_at,
            'last_activity': session.updated_at
        }
    
    def update_session_title_from_content(self, session_id):
        """Auto-generate session title based on first message or files"""
        session = self.session_repo.find_by_id(session_id)
        if not session:
            raise NotFoundError('Session not found')
        
        # Try to get title from first user message
        messages = self.message_repo.find_by_session_id(session_id, limit=5)
        user_messages = [m for m in messages if m.message_type == 'user']
        
        if user_messages:
            first_message = user_messages[0].content[:50]
            title = first_message if len(first_message) < 50 else first_message + "..."
        else:
            # Try to get title from uploaded files
            files = UploadedFile.find_by_session(session_id)[:3]  # Get first 3 files
            if files:
                filenames = [f.original_filename for f in files]
                title = f"Analysis of {', '.join(filenames[:2])}"
                if len(filenames) > 2:
                    title += f" and {len(filenames) - 2} more"
            else:
                title = f"Session {session.created_at.strftime('%Y-%m-%d %H:%M')}"
        
        return self.session_repo.update_session(session_id, {'title': title})