"""
Session model for managing user chat sessions
"""
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import BaseModel


class Session(BaseModel):
    """Session model for storing chat sessions and their metadata"""
    
    __tablename__ = 'sessions'
    
    # Foreign key to user
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    # Session identification
    session_uuid = Column(String(255), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    
    # Session status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    user = relationship('User', back_populates='sessions')
    uploaded_files = relationship('UploadedFile', back_populates='session', lazy='dynamic', cascade='all, delete-orphan')
    chat_messages = relationship('ChatMessage', back_populates='session', lazy='dynamic', cascade='all, delete-orphan')
    analysis_results = relationship('AnalysisResult', back_populates='session', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, user_id, title=None):
        """Initialize session with auto-generated UUID"""
        self.user_id = user_id
        self.session_uuid = str(uuid.uuid4())
        self.title = title or self._generate_default_title()
    
    def _generate_default_title(self):
        """Generate default session title based on current time"""
        now = datetime.utcnow()
        return f"新对话 - {now.strftime('%Y-%m-%d %H:%M')}"
    
    def update_title(self, new_title):
        """Update session title"""
        self.title = new_title
        self.save()
    
    def deactivate(self):
        """Mark session as inactive instead of deleting"""
        self.is_active = False
        self.save()
    
    def get_message_count(self):
        """Get total number of messages in this session"""
        return self.chat_messages.count()
    
    def get_file_count(self):
        """Get total number of uploaded files in this session"""
        return self.uploaded_files.count()
    
    def get_latest_message(self):
        """Get the most recent message in this session"""
        return self.chat_messages.order_by(ChatMessage.created_at.desc()).first()
    
    def to_dict(self, include_stats=True):
        """Convert session to dictionary with optional statistics"""
        result = super().to_dict()
        
        if include_stats:
            result.update({
                'message_count': self.get_message_count(),
                'file_count': self.get_file_count(),
                'latest_activity': self.updated_at.isoformat() if self.updated_at else None
            })
        
        return result
    
    @classmethod
    def find_by_uuid(cls, session_uuid):
        """Find session by UUID"""
        return cls.query.filter_by(session_uuid=session_uuid).first()
    
    @classmethod
    def find_by_user(cls, user_id, active_only=True):
        """Find all sessions for a user"""
        query = cls.query.filter_by(user_id=user_id)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(cls.updated_at.desc()).all()
    
    @classmethod
    def find_recent_by_user(cls, user_id, limit=10):
        """Find recent sessions for a user"""
        return cls.query.filter_by(user_id=user_id, is_active=True)\
                        .order_by(cls.updated_at.desc())\
                        .limit(limit).all()
    
    def __repr__(self):
        return f'<Session {self.session_uuid}>'