"""
Message model for storing chat conversations
"""
from sqlalchemy import Column, String, Integer, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel


class ChatMessage(BaseModel):
    """Model for storing chat messages and AI responses"""
    
    __tablename__ = 'chat_messages'
    
    # Foreign key to session
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False, index=True)
    
    # Message information
    message_type = Column(String(20), nullable=False)  # 'user', 'ai', 'system'
    content = Column(Text, nullable=False)
    content_type = Column(String(20), default='text', nullable=False)  # 'text', 'image', 'thought', 'error'
    
    # Additional message data stored as JSON
    message_metadata = Column(JSON, nullable=True)
    
    # Relationships
    session = relationship('Session', back_populates='chat_messages')
    
    def __init__(self, session_id, message_type, content, content_type='text', message_metadata=None):
        """Initialize chat message"""
        self.session_id = session_id
        self.message_type = message_type
        self.content = content
        self.content_type = content_type
        self.message_metadata = message_metadata or {}
    
    def update_content(self, new_content):
        """Update message content"""
        self.content = new_content
        self.save()
    
    def add_metadata(self, key, value):
        """Add metadata to the message"""
        if not self.message_metadata:
            self.message_metadata = {}
        self.message_metadata[key] = value
        self.save()
    
    def is_user_message(self):
        """Check if message is from user"""
        return self.message_type == 'user'
    
    def is_ai_message(self):
        """Check if message is from AI"""
        return self.message_type == 'ai'
    
    def is_system_message(self):
        """Check if message is system generated"""
        return self.message_type == 'system'
    
    def get_content_preview(self, max_length=100):
        """Get truncated content for preview"""
        if len(self.content) <= max_length:
            return self.content
        return self.content[:max_length] + "..."
    
    def to_dict(self):
        """Convert message to dictionary"""
        result = super().to_dict()
        result['content_preview'] = self.get_content_preview()
        return result
    
    @classmethod
    def find_by_session(cls, session_id, limit=50, offset=0):
        """Find messages for a session with pagination"""
        return cls.query.filter_by(session_id=session_id)\
                        .order_by(cls.created_at.desc())\
                        .limit(limit)\
                        .offset(offset)\
                        .all()
    
    @classmethod
    def find_recent_by_session(cls, session_id, limit=20):
        """Find recent messages for a session"""
        return cls.query.filter_by(session_id=session_id)\
                        .order_by(cls.created_at.desc())\
                        .limit(limit)\
                        .all()
    
    @classmethod
    def search_in_session(cls, session_id, search_term):
        """Search messages within a session"""
        return cls.query.filter_by(session_id=session_id)\
                        .filter(cls.content.contains(search_term))\
                        .order_by(cls.created_at.desc())\
                        .all()
    
    @classmethod
    def count_by_session(cls, session_id):
        """Count total messages in a session"""
        return cls.query.filter_by(session_id=session_id).count()
    
    @classmethod
    def find_by_type(cls, session_id, message_type):
        """Find messages by type within a session"""
        return cls.query.filter_by(session_id=session_id, message_type=message_type)\
                        .order_by(cls.created_at.desc())\
                        .all()
    
    def __repr__(self):
        return f'<ChatMessage {self.message_type}: {self.get_content_preview(30)}>'