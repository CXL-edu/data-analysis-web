"""
Message repository for chat message database operations
"""
from .base_repository import BaseRepository
from database.models import ChatMessage


class MessageRepository(BaseRepository):
    """Repository for ChatMessage model operations"""
    
    def __init__(self):
        super().__init__(ChatMessage)
    
    def create_message(self, session_id, message_type, content, content_type='text', message_metadata=None):
        """Create a new chat message"""
        message = ChatMessage(
            session_id=session_id,
            message_type=message_type,
            content=content,
            content_type=content_type,
            message_metadata=message_metadata
        )
        message.save()
        return message
    
    def find_by_session(self, session_id, limit=50, offset=0):
        """Find messages for a session with pagination"""
        return self.model.find_by_session(session_id, limit, offset)
    
    def find_recent_by_session(self, session_id, limit=20):
        """Find recent messages for a session"""
        return self.model.find_recent_by_session(session_id, limit)
    
    def search_in_session(self, session_id, search_term):
        """Search messages within a session"""
        return self.model.search_in_session(session_id, search_term)
    
    def count_by_session(self, session_id):
        """Count total messages in a session"""
        return self.model.count_by_session(session_id)
    
    def find_by_type(self, session_id, message_type):
        """Find messages by type within a session"""
        return self.model.find_by_type(session_id, message_type)
    
    def get_conversation_history(self, session_id, limit=100):
        """Get conversation history in chronological order"""
        messages = self.model.query.filter_by(session_id=session_id)\
                                  .order_by(self.model.created_at.asc())\
                                  .limit(limit)\
                                  .all()
        return messages
    
    def get_session_message_stats(self, session_id):
        """Get message statistics for a session"""
        from database import db
        
        # Count messages by type
        message_counts = db.session.query(
            ChatMessage.message_type,
            db.func.count(ChatMessage.id).label('count')
        ).filter_by(session_id=session_id)\
         .group_by(ChatMessage.message_type).all()
        
        # Count messages by content type
        content_counts = db.session.query(
            ChatMessage.content_type,
            db.func.count(ChatMessage.id).label('count')
        ).filter_by(session_id=session_id)\
         .group_by(ChatMessage.content_type).all()
        
        total_messages = self.count_by_session(session_id)
        
        return {
            'total_messages': total_messages,
            'messages_by_type': {item.message_type: item.count for item in message_counts},
            'messages_by_content_type': {item.content_type: item.count for item in content_counts}
        }
    
    def get_user_message_stats(self, user_id):
        """Get message statistics for a user across all sessions"""
        from database.models import Session
        from database import db
        
        # Total messages for user
        total_messages = db.session.query(db.func.count(ChatMessage.id))\
                                  .join(Session)\
                                  .filter(Session.user_id == user_id)\
                                  .scalar()
        
        # Messages by type
        message_counts = db.session.query(
            ChatMessage.message_type,
            db.func.count(ChatMessage.id).label('count')
        ).join(Session)\
         .filter(Session.user_id == user_id)\
         .group_by(ChatMessage.message_type).all()
        
        return {
            'total_messages': total_messages or 0,
            'messages_by_type': {item.message_type: item.count for item in message_counts}
        }
    
    def delete_session_messages(self, session_id, user_id=None):
        """Delete all messages for a session with user permission check"""
        if user_id:
            from database.models import Session
            session = Session.query.get(session_id)
            if not session or session.user_id != user_id:
                return False
        
        messages = self.find_all(session_id=session_id)
        count = len(messages)
        
        for message in messages:
            message.delete()
        
        return count
    
    def find_messages_with_images(self, session_id):
        """Find messages containing images"""
        return self.model.query.filter_by(session_id=session_id, content_type='image')\
                              .order_by(self.model.created_at.desc())\
                              .all()
    
    def find_error_messages(self, session_id):
        """Find error messages in a session"""
        return self.model.query.filter_by(session_id=session_id, content_type='error')\
                              .order_by(self.model.created_at.desc())\
                              .all()
    
    def update_message_content(self, message_id, new_content, user_id=None):
        """Update message content with user permission check"""
        message = self.find_by_id(message_id)
        if not message:
            return None
        
        if user_id:
            from database.models import Session
            session = Session.query.get(message.session_id)
            if not session or session.user_id != user_id:
                return None
        
        message.update_content(new_content)
        return message
    
    def add_message_metadata(self, message_id, metadata_key, metadata_value, user_id=None):
        """Add metadata to a message with user permission check"""
        message = self.find_by_id(message_id)
        if not message:
            return None
        
        if user_id:
            from database.models import Session
            session = Session.query.get(message.session_id)
            if not session or session.user_id != user_id:
                return None
        
        message.add_metadata(metadata_key, metadata_value)
        return message
    
    def get_latest_ai_response(self, session_id):
        """Get the most recent AI response in a session"""
        return self.model.query.filter_by(session_id=session_id, message_type='ai')\
                              .order_by(self.model.created_at.desc())\
                              .first()
    
    def export_session_messages(self, session_id, user_id=None):
        """Export all messages from a session for backup/analysis"""
        if user_id:
            from database.models import Session
            session = Session.query.get(session_id)
            if not session or session.user_id != user_id:
                return None
        
        messages = self.get_conversation_history(session_id)
        return [
            {
                'timestamp': msg.created_at.isoformat(),
                'type': msg.message_type,
                'content_type': msg.content_type,
                'content': msg.content,
                'metadata': msg.message_metadata
            }
            for msg in messages
        ]