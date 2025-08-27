"""
API version 1 namespaces and registration
"""
from flask_restx import Namespace


def register_namespaces(api):
    """Register all API namespaces"""
    from .auth import auth_ns
    from .sessions import sessions_ns
    from .files import files_ns
    from .chat import chat_ns
    from .analysis import analysis_ns
    from .health import health_ns
    
    api.add_namespace(health_ns, path='/health')
    api.add_namespace(auth_ns, path='/auth')
    api.add_namespace(sessions_ns, path='/sessions')
    api.add_namespace(files_ns, path='/files')
    api.add_namespace(chat_ns, path='/chat')
    api.add_namespace(analysis_ns, path='/analysis')