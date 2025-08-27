"""
Data analysis API endpoints
"""
from flask import request, jsonify, Response
from flask_restx import Namespace, Resource
from app.utils.decorators import require_auth, require_session_owner_by_uuid, validate_json
from app.api.schemas.analysis_schemas import AnalysisRequestSchema
from app.services.analysis_service import AnalysisService
from app.utils.exceptions import ValidationError, NotFoundError
import json

analysis_ns = Namespace('analysis', description='Data analysis operations')

@analysis_ns.route('/<string:session_uuid>/analyze')
class AnalyzeDataResource(Resource):
    @require_auth
    @require_session_owner_by_uuid
    @validate_json(AnalysisRequestSchema)
    def post(self, session_uuid):
        """Perform data analysis on session files"""
        try:
            analysis_service = AnalysisService()
            
            analysis_type = request.validated_data['analysis_type']
            file_ids = request.validated_data.get('file_ids', [])
            parameters = request.validated_data.get('parameters', {})
            
            # Validate that user has access to all specified files
            session_file_ids = [f.id for f in request.current_session.uploaded_files]
            if file_ids and not all(fid in session_file_ids for fid in file_ids):
                return {'error': 'One or more files not found in this session'}, 400
            
            # If no specific files provided, use all files in session
            if not file_ids:
                file_ids = session_file_ids
            
            # Perform analysis
            result = analysis_service.perform_analysis(
                session_id=request.current_session.id,
                analysis_type=analysis_type,
                file_ids=file_ids,
                parameters=parameters
            )
            
            return {
                'analysis_result': {
                    'id': result.id,
                    'analysis_type': result.analysis_type,
                    'result_data': result.result_data,
                    'created_at': result.created_at.isoformat()
                }
            }, 201
            
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': 'Analysis failed'}, 500

@analysis_ns.route('/<string:session_uuid>/analyze/stream')
class StreamAnalysisResource(Resource):
    @require_auth
    @require_session_owner_by_uuid
    def post(self, session_uuid):
        """Stream data analysis results"""
        try:
            # Validate JSON input
            if not request.is_json:
                return {'error': 'Content-Type must be application/json'}, 400
            
            data = request.get_json()
            analysis_type = data.get('analysis_type')
            file_ids = data.get('file_ids', [])
            parameters = data.get('parameters', {})
            
            if not analysis_type:
                return {'error': 'Analysis type is required'}, 400
            
            analysis_service = AnalysisService()
            
            def generate_analysis():
                try:
                    # Validate that user has access to all specified files
                    session_file_ids = [f.id for f in request.current_session.uploaded_files]
                    if file_ids and not all(fid in session_file_ids for fid in file_ids):
                        yield f"data: {json.dumps({'type': 'error', 'error': 'One or more files not found in this session'})}\n\n"
                        return
                    
                    # If no specific files provided, use all files in session
                    if not file_ids:
                        file_ids = session_file_ids
                    
                    if not file_ids:
                        yield f"data: {json.dumps({'type': 'error', 'error': 'No files found in session'})}\n\n"
                        return
                    
                    # Send start event
                    yield f"data: {json.dumps({'type': 'analysis_start', 'analysis_type': analysis_type})}\n\n"
                    
                    # Stream analysis results
                    result_data = {}
                    for step_result in analysis_service.stream_analysis(
                        session_id=request.current_session.id,
                        analysis_type=analysis_type,
                        file_ids=file_ids,
                        parameters=parameters
                    ):
                        result_data.update(step_result)
                        yield f"data: {json.dumps({'type': 'analysis_step', 'data': step_result})}\n\n"
                    
                    # Save final result
                    final_result = analysis_service.save_analysis_result(
                        session_id=request.current_session.id,
                        analysis_type=analysis_type,
                        result_data=result_data
                    )
                    
                    # Send completion event
                    yield f"data: {json.dumps({'type': 'analysis_complete', 'result': {'id': final_result.id, 'analysis_type': final_result.analysis_type, 'result_data': final_result.result_data, 'created_at': final_result.created_at.isoformat()}})}\n\n"
                    
                except Exception as e:
                    print(f"Error in analysis stream: {e}")
                    yield f"data: {json.dumps({'type': 'error', 'error': 'Analysis failed'})}\n\n"
                
                yield "data: [DONE]\n\n"
            
            return Response(
                generate_analysis(),
                mimetype='text/plain',
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'X-Accel-Buffering': 'no'
                }
            )
            
        except Exception as e:
            return {'error': 'Failed to start analysis stream'}, 500

@analysis_ns.route('/<string:session_uuid>/results')
class AnalysisResultsResource(Resource):
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
            } for result in sorted(session.analysis_results, key=lambda x: x.created_at, reverse=True)]
            
            return {'results': results}, 200
        except Exception as e:
            return {'error': 'Failed to retrieve analysis results'}, 500

@analysis_ns.route('/results/<int:result_id>')
class AnalysisResultResource(Resource):
    @require_auth
    def get(self, result_id):
        """Get a specific analysis result"""
        try:
            analysis_service = AnalysisService()
            result = analysis_service.get_result_by_id(result_id)
            
            # Check if user owns the session that contains this result
            if result.session.user_id != request.current_user.id:
                return {'error': 'Access denied'}, 403
            
            return {
                'result': {
                    'id': result.id,
                    'analysis_type': result.analysis_type,
                    'result_data': result.result_data,
                    'created_at': result.created_at.isoformat(),
                    'session_uuid': result.session.uuid
                }
            }, 200
        except NotFoundError as e:
            return {'error': str(e)}, 404
        except Exception as e:
            return {'error': 'Failed to retrieve analysis result'}, 500
    
    @require_auth
    def delete(self, result_id):
        """Delete a specific analysis result"""
        try:
            analysis_service = AnalysisService()
            result = analysis_service.get_result_by_id(result_id)
            
            # Check if user owns the session that contains this result
            if result.session.user_id != request.current_user.id:
                return {'error': 'Access denied'}, 403
            
            analysis_service.delete_result(result_id)
            return {'message': 'Analysis result deleted successfully'}, 200
        except NotFoundError as e:
            return {'error': str(e)}, 404
        except Exception as e:
            return {'error': 'Failed to delete analysis result'}, 500

@analysis_ns.route('/types')
class AnalysisTypesResource(Resource):
    def get(self):
        """Get available analysis types"""
        return {
            'analysis_types': [
                {
                    'type': 'descriptive_stats',
                    'name': 'Descriptive Statistics',
                    'description': 'Calculate basic statistics (mean, median, mode, etc.)'
                },
                {
                    'type': 'correlation_analysis',
                    'name': 'Correlation Analysis',
                    'description': 'Analyze correlations between variables'
                },
                {
                    'type': 'data_profiling',
                    'name': 'Data Profiling',
                    'description': 'Profile data quality and structure'
                },
                {
                    'type': 'visualization',
                    'name': 'Data Visualization',
                    'description': 'Generate charts and graphs'
                },
                {
                    'type': 'anomaly_detection',
                    'name': 'Anomaly Detection',
                    'description': 'Detect outliers and anomalies in data'
                },
                {
                    'type': 'time_series',
                    'name': 'Time Series Analysis',
                    'description': 'Analyze time-based data patterns'
                }
            ]
        }, 200