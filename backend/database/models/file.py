"""
File model for managing uploaded files
"""
import os
from sqlalchemy import Column, String, Integer, BigInteger, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import BaseModel


class UploadedFile(BaseModel):
    """Model for storing information about uploaded files"""
    
    __tablename__ = 'uploaded_files'
    
    # Foreign key to session
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False, index=True)
    
    # File information
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    file_type = Column(String(50), nullable=False)
    
    # Analysis status
    analysis_status = Column(String(20), default='pending', nullable=False)
    
    # Relationships
    session = relationship('Session', back_populates='uploaded_files')
    
    def __init__(self, session_id, original_filename, stored_filename, file_path, file_size, file_type):
        """Initialize uploaded file record"""
        self.session_id = session_id
        self.original_filename = original_filename
        self.stored_filename = stored_filename
        self.file_path = file_path
        self.file_size = file_size
        self.file_type = file_type
    
    def update_analysis_status(self, status):
        """Update analysis status"""
        valid_statuses = ['pending', 'analyzing', 'completed', 'failed']
        if status in valid_statuses:
            self.analysis_status = status
            self.save()
        else:
            raise ValueError(f"Invalid analysis status: {status}")
    
    def get_file_size_mb(self):
        """Get file size in MB"""
        return round(self.file_size / (1024 * 1024), 2)
    
    def file_exists(self):
        """Check if the physical file still exists"""
        return os.path.exists(self.file_path)
    
    def delete_file(self):
        """Delete the physical file and database record"""
        if self.file_exists():
            try:
                os.remove(self.file_path)
            except OSError as e:
                print(f"Error deleting file {self.file_path}: {e}")
        
        self.delete()
    
    def to_dict(self):
        """Convert file record to dictionary"""
        result = super().to_dict()
        result.update({
            'file_size_mb': self.get_file_size_mb(),
            'file_exists': self.file_exists()
        })
        return result
    
    @classmethod
    def find_by_session(cls, session_id):
        """Find all files for a session"""
        return cls.query.filter_by(session_id=session_id)\
                        .order_by(cls.created_at.desc()).all()
    
    @classmethod
    def find_by_status(cls, status, session_id=None):
        """Find files by analysis status"""
        query = cls.query.filter_by(analysis_status=status)
        if session_id:
            query = query.filter_by(session_id=session_id)
        return query.all()
    
    @classmethod
    def get_total_size_by_user(cls, user_id):
        """Get total file size for a user across all sessions"""
        from .session import Session
        return db.session.query(db.func.sum(cls.file_size))\
                         .join(Session)\
                         .filter(Session.user_id == user_id)\
                         .scalar() or 0
    
    def __repr__(self):
        return f'<UploadedFile {self.original_filename}>'