"""
Session management API endpoints
"""
from flask import request, jsonify
from flask_restx import Namespace, Resource
from app.utils.decorators import require_auth, require_session_owner_by_uuid, validate_json
from app.api.schemas.session_schemas import CreateSessionSchema, UpdateSessionSchema
from app.services.session_service import SessionService
from app.utils.exceptions import ValidationError, NotFoundError, AuthorizationError

sessions_ns = Namespace('sessions', description='Session management operations')

@sessions_ns.route('/')
class SessionListResource(Resource):
    def options(self):
        """Handle preflight request for sessions list"""
        from flask import make_response
        response = make_response({})
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

    @require_auth
    def get(self):
        """Get all sessions for current user"""
        try:
            print(f"Sessions GET request for user: {request.current_user.id}")
            session_service = SessionService()
            sessions = session_service.get_user_sessions(request.current_user.id)
            
            print(f"Raw sessions from service: {sessions}")
            print(f"Sessions type: {type(sessions)}")
            print(f"Found {len(sessions)} sessions for user {request.current_user.id}")
            
            session_list = []
            for session in sessions:
                print(f"Processing session: {session.id} - {session.title}")
                try:
                    message_count = session.chat_messages.count()
                    file_count = session.uploaded_files.count()
                    print(f"Session {session.id}: messages={message_count}, files={file_count}")
                except Exception as count_error:
                    print(f"Error counting for session {session.id}: {count_error}")
                    message_count = 0
                    file_count = 0
                
                session_data = {
                    'id': session.id,
                    'uuid': session.session_uuid,
                    'title': session.title,
                    'created_at': session.created_at.isoformat(),
                    'updated_at': session.updated_at.isoformat(),
                    'is_active': session.is_active,
                    'message_count': message_count,
                    'file_count': file_count
                }
                session_list.append(session_data)
                print(f"Added session data: {session_data}")
            
            print(f"Final session list: {session_list}")
            return session_list, 200
        except Exception as e:
            print(f"Error in sessions endpoint: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'error': f'Failed to retrieve sessions: {str(e)}'}, 500
    
    @require_auth
    def post(self):
        """Create a new session"""
        print(f"Session creation request for user: {request.current_user.id}")
        print(f"Request data: {request.json}")
        print(f"Validated data: {getattr(request, 'validated_data', 'No validated data')}")
        
        try:
            session_service = SessionService()
            # Get title from request data, fallback to default
            title = None
            if request.json:
                title = request.json.get('title')
            title = title or 'New Session'
            print(f"Creating session with title: '{title}'")
            
            session = session_service.create_session(
                request.current_user.id, 
                title
            )
            
            print(f"Session created successfully: {session.id} - {session.session_uuid}")
            
            response_data = {
                'id': session.id,
                'uuid': session.session_uuid,
                'title': session.title,
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat(),
                'is_active': session.is_active
            }
            
            print(f"Returning session data: {response_data}")
            return response_data, 201
        except Exception as e:
            print(f"Session creation failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'error': f'Failed to create session: {str(e)}'}, 500

@sessions_ns.route('/<string:session_uuid>')
class SessionResource(Resource):
    @require_auth
    @require_session_owner_by_uuid
    def get(self, session_uuid):
        """Get session details with all messages and files"""
        try:
            session = request.current_session
            
            return {
                'session': {
                    'uuid': session.session_uuid,
                    'title': session.title,
                    'created_at': session.created_at.isoformat(),
                    'updated_at': session.updated_at.isoformat(),
                    'chat_messages': [{
                        'id': msg.id,
                        'message_type': msg.message_type,
                        'content': msg.content,
                        'timestamp': msg.timestamp.isoformat()
                    } for msg in session.chat_messages],
                    'uploaded_files': [{
                        'id': file.id,
                        'filename': file.filename,
                        'file_path': file.file_path,
                        'file_size': file.file_size,
                        'mime_type': file.mime_type,
                        'upload_timestamp': file.upload_timestamp.isoformat()
                    } for file in session.uploaded_files],
                    'analysis_results': [{
                        'id': result.id,
                        'analysis_type': result.analysis_type,
                        'result_data': result.result_data,
                        'created_at': result.created_at.isoformat()
                    } for result in session.analysis_results]
                }
            }, 200
        except Exception as e:
            return {'error': 'Failed to retrieve session details'}, 500
    
    @require_auth
    @require_session_owner_by_uuid
    @validate_json(UpdateSessionSchema)
    def put(self, session_uuid):
        """Update session details"""
        try:
            session_service = SessionService()
            session = session_service.update_session(
                request.current_session.id,
                request.validated_data
            )
            
            return {
                'session': {
                    'uuid': session.session_uuid,
                    'title': session.title,
                    'created_at': session.created_at.isoformat(),
                    'updated_at': session.updated_at.isoformat()
                }
            }, 200
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': 'Failed to update session'}, 500
    
    @require_auth
    @require_session_owner_by_uuid
    def delete(self, session_uuid):
        """Delete session and all associated data"""
        try:
            session_service = SessionService()
            session_service.delete_session(request.current_session.id)
            
            return {'message': 'Session deleted successfully'}, 200
        except Exception as e:
            return {'error': 'Failed to delete session'}, 500

@sessions_ns.route('/<string:session_uuid>/messages')
class SessionMessagesResource(Resource):
    @require_auth
    @require_session_owner_by_uuid
    def get(self, session_uuid):
        """Get all messages for a session"""
        try:
            session = request.current_session
            messages = [{
                'id': msg.id,
                'message_type': msg.message_type,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat()
            } for msg in session.chat_messages]
            
            return {'messages': messages}, 200
        except Exception as e:
            return {'error': 'Failed to retrieve messages'}, 500

@sessions_ns.route('/<string:session_uuid>/files')
class SessionFilesResource(Resource):
    @require_auth
    @require_session_owner_by_uuid
    def get(self, session_uuid):
        """Get all files for a session"""
        try:
            session = request.current_session
            files = [{
                'id': file.id,
                'filename': file.filename,
                'file_path': file.file_path,
                'file_size': file.file_size,
                'mime_type': file.mime_type,
                'upload_timestamp': file.upload_timestamp.isoformat()
            } for file in session.uploaded_files]
            
            return {'files': files}, 200
        except Exception as e:
            return {'error': 'Failed to retrieve files'}, 500

@sessions_ns.route('/<string:session_uuid>/analysis')
class SessionAnalysisResource(Resource):
    @require_auth
    @require_session_owner_by_uuid
    def get(self, session_uuid):
        """Get all analysis results for a session"""
        try:
            session = request.current_session
            results = [{
                'id': result.id,
                'analysis_type': result.analysis_type,
                'result_data': result.result_data,
                'created_at': result.created_at.isoformat()
            } for result in session.analysis_results]
            
            return {'analysis_results': results}, 200
        except Exception as e:
            return {'error': 'Failed to retrieve analysis results'}, 500

@sessions_ns.route('/<string:session_uuid>/clear')
class SessionClearResource(Resource):
    @require_auth
    @require_session_owner_by_uuid
    def post(self, session_uuid):
        """Clear all messages and files from session (keep session itself)"""
        try:
            session_service = SessionService()
            session_service.clear_session_data(request.current_session.id)
            
            return {'message': 'Session data cleared successfully'}, 200
        except Exception as e:
            return {'error': 'Failed to clear session data'}, 500