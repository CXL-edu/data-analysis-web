"""
Health check API endpoint
"""
from flask import jsonify
from flask_restx import Namespace, Resource
from datetime import datetime

health_ns = Namespace('health', description='Health check operations')

@health_ns.route('')
class HealthResource(Resource):
    def get(self):
        """Health check endpoint"""
        return {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'AI Data Assistant Backend',
            'version': '1.0.0'
        }, 200