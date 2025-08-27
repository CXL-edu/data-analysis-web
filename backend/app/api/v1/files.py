"""
File upload API endpoints - SIMPLIFIED
"""
import os
from flask import request
from flask_restx import Namespace, Resource
from werkzeug.utils import secure_filename
from app.utils.decorators import require_auth, require_session_owner_by_uuid
from app.services.file_service import FileService
from app.utils.exceptions import ValidationError

files_ns = Namespace('files', description='File upload operations')

@files_ns.route('/upload/<string:session_uuid>')
class FileUploadResource(Resource):
    def options(self, session_uuid):
        """Handle preflight request"""
        from flask import make_response
        response = make_response({})
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    
    @require_auth
    @require_session_owner_by_uuid
    def post(self, session_uuid):
        """Upload a file to a session"""
        print(f"File upload request for session: {session_uuid}")
        
        try:
            if 'file' not in request.files:
                return {'error': 'No file provided'}, 400
            
            file = request.files['file']
            if file.filename == '':
                return {'error': 'No file selected'}, 400
            
            # Use FileService to handle upload
            file_service = FileService()
            uploaded_file = file_service.upload_file(
                file, 
                request.current_session.id,
                request.current_user.id
            )
            
            print(f"File uploaded successfully: {uploaded_file.original_filename}")
            
            # Try to get preview data
            preview_data = None
            try:
                preview_data = file_service.get_file_preview(uploaded_file)
                print(f"Preview data generated: {len(preview_data.get('data', []))} rows")
            except Exception as e:
                print(f"Preview generation failed: {e}")
            
            return {
                'session_id': request.current_session.session_uuid,
                'filename': uploaded_file.original_filename,
                'message': 'File uploaded successfully',
                'preview_data': preview_data.get('data', []) if preview_data else [],
                'columns': preview_data.get('columns', []) if preview_data else [],
                'stats': preview_data.get('stats', {}) if preview_data else {}
            }, 201
            
        except ValidationError as e:
            print(f"Validation error: {e}")
            return {'error': str(e)}, 400
        except Exception as e:
            print(f"File upload error: {e}")
            import traceback
            traceback.print_exc()
            return {'error': f'Upload failed: {str(e)}'}, 500