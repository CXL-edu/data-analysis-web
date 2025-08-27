"""
Database module for AI Data Assistant
Contains models, repositories, and database-related utilities
"""
from flask_sqlalchemy import SQLAlchemy

# Database instance will be initialized in app factory
db = SQLAlchemy()