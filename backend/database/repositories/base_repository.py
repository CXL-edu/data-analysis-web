"""
Base repository with common CRUD operations
"""
from database import db


class BaseRepository:
    """Base repository class with generic CRUD operations"""
    
    def __init__(self, model):
        self.model = model
    
    def create(self, **kwargs):
        """Create a new record"""
        instance = self.model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance
    
    def find_by_id(self, id):
        """Find record by ID"""
        return self.model.query.get(id)
    
    def find_all(self, **filters):
        """Find all records with optional filters"""
        query = self.model.query
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.all()
    
    def find_one(self, **filters):
        """Find single record with filters"""
        query = self.model.query
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.first()
    
    def update(self, id, **kwargs):
        """Update record by ID"""
        instance = self.find_by_id(id)
        if instance:
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            db.session.commit()
            return instance
        return None
    
    def delete(self, id):
        """Delete record by ID"""
        instance = self.find_by_id(id)
        if instance:
            db.session.delete(instance)
            db.session.commit()
            return True
        return False
    
    def count(self, **filters):
        """Count records with optional filters"""
        query = self.model.query
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.count()
    
    def paginate(self, page=1, per_page=20, **filters):
        """Paginate records with optional filters"""
        query = self.model.query
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
    
    def exists(self, **filters):
        """Check if record exists with given filters"""
        return self.find_one(**filters) is not None