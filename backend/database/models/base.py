"""
Base model class with common functionality
"""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from app.extensions import db


class BaseModel(db.Model):
    """Base model class with common columns and methods"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def save(self):
        """Save the model to database"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """Delete the model from database"""
        db.session.delete(self)
        db.session.commit()
    
    def update(self, **kwargs):
        """Update model attributes"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return self
    
    def to_dict(self):
        """Convert model to dictionary"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result
    
    @classmethod
    def find_by_id(cls, id):
        """Find record by ID"""
        return cls.query.get(id)
    
    @classmethod
    def find_all(cls):
        """Find all records"""
        return cls.query.all()