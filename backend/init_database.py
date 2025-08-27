#!/usr/bin/env python3
"""
Database initialization script for AI Data Assistant
"""

import os
import sys
from app import create_app
from app.extensions import db
from database.models import User, Session, UploadedFile, ChatMessage, AnalysisResult


def init_database():
    """Initialize database tables"""
    print("=" * 60)
    print("🗄️ AI Data Assistant - Database Initialization")
    print("=" * 60)
    
    # Get configuration from environment
    config_name = os.environ.get('FLASK_CONFIG', 'development')
    
    # Create Flask app
    app = create_app(config_name)
    
    with app.app_context():
        try:
            print(f"📊 Configuration: {config_name}")
            print(f"🔗 Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')}")
            print()
            
            # Drop all tables if they exist (for development)
            if config_name == 'development':
                print("🗑️ Dropping existing tables (development mode)...")
                db.drop_all()
                print("✅ Tables dropped successfully")
            
            # Create all tables
            print("🏗️ Creating database tables...")
            db.create_all()
            print("✅ Tables created successfully")
            
            # Print table information
            print()
            print("📋 Created tables:")
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            for table in tables:
                print(f"  - {table}")
            
            print()
            print("=" * 60)
            print("🎉 Database initialization completed successfully!")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            sys.exit(1)


def create_test_user():
    """Create a test user for development"""
    print("👤 Creating test user...")
    
    config_name = os.environ.get('FLASK_CONFIG', 'development')
    app = create_app(config_name)
    
    with app.app_context():
        try:
            from database.repositories.user_repository import UserRepository
            user_repo = UserRepository()
            
            # Check if test user already exists
            existing_user = user_repo.find_by_email('test@example.com')
            if existing_user:
                print("⚠️ Test user already exists")
                return existing_user
            
            # Create test user
            test_user = user_repo.create_user(
                username='testuser',
                email='test@example.com',
                password='testpass123'
            )
            
            # Mark email as verified for testing
            test_user.is_email_verified = True
            test_user.save()
            
            print(f"✅ Test user created:")
            print(f"   Email: test@example.com")
            print(f"   Password: testpass123")
            print(f"   Username: testuser")
            
            return test_user
            
        except Exception as e:
            print(f"❌ Error creating test user: {e}")
            return None


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test-user':
        create_test_user()
    else:
        init_database()
        if os.environ.get('FLASK_CONFIG', 'development') == 'development':
            create_test_user()