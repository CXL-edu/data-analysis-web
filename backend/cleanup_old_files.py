#!/usr/bin/env python3
"""
Clean up old and unused files from the app directory
"""

import os

def cleanup_old_files():
    """Remove old and unused files"""
    
    files_to_remove = [
        # Old API routes file (replaced by v1 API)
        'app/api/routes.py',
        
        # Duplicate/temporary service files
        'app/services/chat_service_new.py',
        
        # Old service files (functionality moved to new modular services)
        'app/services/chart_generator.py',
        'app/services/data_analyzer.py', 
        'app/services/file_handler.py',
        
        # Unused utility files
        'app/utils/json_encoder.py',
        'app/utils/session_manager.py'
    ]
    
    print("🧹 Cleaning up old and unused files...")
    print("=" * 50)
    
    for file_path in files_to_remove:
        full_path = os.path.join(os.getcwd(), file_path)
        
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
                print(f"✅ Deleted: {file_path}")
            except OSError as e:
                print(f"❌ Error deleting {file_path}: {e}")
        else:
            print(f"⚠️  Not found: {file_path}")
    
    print("=" * 50)
    print("🎉 Cleanup completed!")
    
    # Show remaining structure
    print("\n📁 Current app structure:")
    show_directory_structure('app', max_depth=3)

def show_directory_structure(path, max_depth=2, current_depth=0):
    """Show directory structure"""
    if current_depth >= max_depth:
        return
    
    try:
        items = sorted(os.listdir(path))
        for item in items:
            item_path = os.path.join(path, item)
            indent = "  " * current_depth
            
            if os.path.isdir(item_path):
                print(f"{indent}📁 {item}/")
                show_directory_structure(item_path, max_depth, current_depth + 1)
            else:
                if item.endswith('.py'):
                    print(f"{indent}📄 {item}")
    except OSError:
        pass

if __name__ == '__main__':
    cleanup_old_files()