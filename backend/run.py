#!/usr/bin/env python3
"""
Main entry point for AI Data Assistant Backend
"""

import os
import sys
from app import create_app
from app.config import config

def main():
    """Main function to start the Flask application"""
    
    print("=" * 60)
    print("🚀 AI Data Analysis Assistant - Backend Server")
    print("=" * 60)
    
    # Get configuration from environment
    config_name = os.environ.get('FLASK_CONFIG', 'development')
    
    # Create Flask app with selected configuration
    app = create_app(config_name)
    
    print(f"📊 Configuration: {config_name}")
    print(f"🌐 Server URL: http://localhost:5000")
    print(f"📡 API Base: http://localhost:5000/api/v1")
    print(f"📖 API Docs: http://localhost:5000/api/docs/")
    print()
    print("📋 Available API endpoints:")
    print("  Authentication:")
    print("    - POST /api/v1/auth/register    - User registration")
    print("    - POST /api/v1/auth/login       - User login")
    print("    - GET  /api/v1/auth/profile     - Get user profile")
    print("  Sessions:")
    print("    - GET  /api/v1/sessions         - Get all sessions")
    print("    - POST /api/v1/sessions         - Create new session")
    print("    - GET  /api/v1/sessions/<uuid>  - Get session details")
    print("  Files:")
    print("    - POST /api/v1/files/upload/<uuid> - Upload file to session")
    print("    - GET  /api/v1/files/<id>       - Download file")
    print("  Chat:")
    print("    - POST /api/v1/chat/<uuid>/stream - Stream chat response")
    print("  Analysis:")
    print("    - POST /api/v1/analysis/<uuid>/analyze - Perform analysis")
    print("=" * 60)
    print()
    
    try:
        app.run(
            debug=app.config.get('DEBUG', False),
            host='0.0.0.0',
            port=5000,
            use_reloader=app.config.get('DEBUG', False)
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down server...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()