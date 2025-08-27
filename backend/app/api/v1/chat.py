"""
Chat and messaging API endpoints
"""
from flask import request, Response, jsonify, stream_template
from flask_restx import Namespace, Resource
from app.utils.decorators import require_auth, require_session_owner_by_uuid, validate_json
from app.api.schemas.chat_schemas import SendMessageSchema
from app.services.chat_service import ChatService
from app.utils.exceptions import ValidationError, NotFoundError
import json

chat_ns = Namespace('chat', description='Chat and messaging operations')

@chat_ns.route('/<string:session_uuid>/send')
class SendMessageResource(Resource):
    @require_auth
    @require_session_owner_by_uuid
    @validate_json(SendMessageSchema)
    def post(self, session_uuid):
        """Send a message in a chat session"""
        try:
            chat_service = ChatService()
            
            # Save user message
            user_message = chat_service.save_message(
                session_id=request.current_session.id,
                message_type='user',
                content=request.validated_data['message']
            )
            
            # Generate AI response (this will be handled by the streaming endpoint)
            return {
                'message': {
                    'id': user_message.id,
                    'message_type': user_message.message_type,
                    'content': user_message.content,
                    'timestamp': user_message.timestamp.isoformat()
                }
            }, 201
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': 'Failed to send message'}, 500

@chat_ns.route('/<string:session_uuid>/stream')
class StreamChatResource(Resource):
    @require_auth
    @require_session_owner_by_uuid
    def post(self, session_uuid):
        """Stream AI response for a chat session"""
        try:
            # Validate JSON input
            if not request.is_json:
                return {'error': 'Content-Type must be application/json'}, 400
            
            data = request.get_json()
            if 'message' not in data:
                return {'error': 'Message is required'}, 400
            
            chat_service = ChatService()
            
            def generate_response():
                try:
                    # Save user message first
                    user_message = chat_service.save_message(
                        session_id=request.current_session.id,
                        message_type='user',
                        content=data['message']
                    )
                    
                    # Send user message event
                    yield f"data: {json.dumps({'type': 'user_message', 'message': {'id': user_message.id, 'content': user_message.content, 'timestamp': user_message.timestamp.isoformat()}})}\n\n"
                    
                    # Generate AI response with streaming
                    ai_response_content = ""
                    for chunk in chat_service.generate_ai_response(
                        session_id=request.current_session.id,
                        message=data['message'],
                        session_files=request.current_session.uploaded_files
                    ):
                        ai_response_content += chunk
                        yield f"data: {json.dumps({'type': 'ai_chunk', 'chunk': chunk})}\n\n"
                    
                    # Save complete AI response
                    ai_message = chat_service.save_message(
                        session_id=request.current_session.id,
                        message_type='ai',
                        content=ai_response_content
                    )
                    
                    # Send completion event
                    yield f"data: {json.dumps({'type': 'ai_complete', 'message': {'id': ai_message.id, 'content': ai_message.content, 'timestamp': ai_message.timestamp.isoformat()}})}\n\n"
                    
                except Exception as e:
                    print(f"Error in chat stream: {e}")
                    yield f"data: {json.dumps({'type': 'error', 'error': 'Failed to generate response'})}\n\n"
                
                yield "data: [DONE]\n\n"
            
            return Response(
                generate_response(),
                mimetype='text/plain',
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'X-Accel-Buffering': 'no'
                }
            )
            
        except Exception as e:
            return {'error': 'Failed to start chat stream'}, 500

@chat_ns.route('/<string:session_uuid>/messages')
class SessionMessagesResource(Resource):
    @require_auth
    @require_session_owner_by_uuid
    def get(self, session_uuid):
        """Get all messages in a session"""
        try:
            session = request.current_session
            messages = [{
                'id': msg.id,
                'message_type': msg.message_type,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat()
            } for msg in sorted(session.chat_messages, key=lambda x: x.timestamp)]
            
            return {'messages': messages}, 200
        except Exception as e:
            return {'error': 'Failed to retrieve messages'}, 500

@chat_ns.route('/messages/<int:message_id>')
class MessageResource(Resource):
    @require_auth
    def get(self, message_id):
        """Get a specific message"""
        try:
            chat_service = ChatService()
            message = chat_service.get_message_by_id(message_id)
            
            # Check if user owns the session that contains this message
            if message.session.user_id != request.current_user.id:
                return {'error': 'Access denied'}, 403
            
            return {
                'message': {
                    'id': message.id,
                    'message_type': message.message_type,
                    'content': message.content,
                    'timestamp': message.timestamp.isoformat(),
                    'session_uuid': message.session.uuid
                }
            }, 200
        except NotFoundError as e:
            return {'error': str(e)}, 404
        except Exception as e:
            return {'error': 'Failed to retrieve message'}, 500
    
    @require_auth
    def delete(self, message_id):
        """Delete a specific message"""
        try:
            chat_service = ChatService()
            message = chat_service.get_message_by_id(message_id)
            
            # Check if user owns the session that contains this message
            if message.session.user_id != request.current_user.id:
                return {'error': 'Access denied'}, 403
            
            chat_service.delete_message(message_id)
            return {'message': 'Message deleted successfully'}, 200
        except NotFoundError as e:
            return {'error': str(e)}, 404
        except Exception as e:
            return {'error': 'Failed to delete message'}, 500

@chat_ns.route('/<string:session_uuid>/clear')
class ClearChatResource(Resource):
    @require_auth
    @require_session_owner_by_uuid
    def post(self, session_uuid):
        """Clear all messages in a session"""
        try:
            chat_service = ChatService()
            chat_service.clear_session_messages(request.current_session.id)
            
            return {'message': 'All messages cleared successfully'}, 200
        except Exception as e:
            return {'error': 'Failed to clear messages'}, 500