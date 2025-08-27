import os

# Files to delete
files = [
    'app/api/routes.py',
    'app/services/chat_service_new.py',
    'app/services/chart_generator.py',
    'app/services/data_analyzer.py',
    'app/services/file_handler.py',
    'app/utils/json_encoder.py',
    'app/utils/session_manager.py'
]

for file in files:
    if os.path.exists(file):
        os.remove(file)
        print(f"Deleted: {file}")
    else:
        print(f"Not found: {file}")