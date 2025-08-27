"""
Analysis repository for analysis result database operations
"""
from .base_repository import BaseRepository
from database.models import AnalysisResult


class AnalysisRepository(BaseRepository):
    """Repository for AnalysisResult model operations"""
    
    def __init__(self):
        super().__init__(AnalysisResult)
    
    def create_analysis_result(self, session_id, analysis_type, results):
        """Create a new analysis result"""
        analysis = AnalysisResult(
            session_id=session_id,
            analysis_type=analysis_type,
            results=results
        )
        analysis.save()
        return analysis
    
    def find_by_session(self, session_id):
        """Find all analysis results for a session"""
        return self.model.find_by_session(session_id)
    
    def find_by_type(self, session_id, analysis_type):
        """Find analysis results by type for a session"""
        return self.model.find_by_type(session_id, analysis_type)
    
    def find_latest_by_session(self, session_id):
        """Find the most recent analysis result for a session"""
        return self.model.find_latest_by_session(session_id)
    
    def get_analysis_types_for_session(self, session_id):
        """Get all analysis types that have been run for a session"""
        return self.model.get_analysis_types_for_session(session_id)
    
    def count_by_session(self, session_id):
        """Count total analysis results for a session"""
        return self.model.count_by_session(session_id)
    
    def update_analysis_results(self, analysis_id, new_results, user_id=None):
        """Update analysis results with user permission check"""
        analysis = self.find_by_id(analysis_id)
        if not analysis:
            return None
        
        if user_id:
            from database.models import Session
            session = Session.query.get(analysis.session_id)
            if not session or session.user_id != user_id:
                return None
        
        analysis.update_results(new_results)
        return analysis
    
    def get_session_analysis_summary(self, session_id):
        """Get analysis summary for a session"""
        analyses = self.find_by_session(session_id)
        
        if not analyses:
            return {
                'total_analyses': 0,
                'analysis_types': [],
                'successful_analyses': 0,
                'failed_analyses': 0,
                'latest_analysis': None
            }
        
        successful = sum(1 for a in analyses if a.is_successful())
        failed = len(analyses) - successful
        analysis_types = list(set(a.analysis_type for a in analyses))
        latest = max(analyses, key=lambda a: a.created_at) if analyses else None
        
        return {
            'total_analyses': len(analyses),
            'analysis_types': analysis_types,
            'successful_analyses': successful,
            'failed_analyses': failed,
            'latest_analysis': latest.to_dict() if latest else None
        }
    
    def get_user_analysis_stats(self, user_id):
        """Get analysis statistics for a user across all sessions"""
        from database.models import Session
        from database import db
        
        # Total analyses for user
        total_analyses = db.session.query(db.func.count(AnalysisResult.id))\
                                  .join(Session)\
                                  .filter(Session.user_id == user_id)\
                                  .scalar()
        
        # Analyses by type
        analysis_counts = db.session.query(
            AnalysisResult.analysis_type,
            db.func.count(AnalysisResult.id).label('count')
        ).join(Session)\
         .filter(Session.user_id == user_id)\
         .group_by(AnalysisResult.analysis_type).all()
        
        return {
            'total_analyses': total_analyses or 0,
            'analyses_by_type': {item.analysis_type: item.count for item in analysis_counts}
        }
    
    def find_failed_analyses(self, session_id=None):
        """Find analyses that failed"""
        query = self.model.query
        if session_id:
            query = query.filter_by(session_id=session_id)
        
        # Filter for analyses with error in results
        failed_analyses = []
        for analysis in query.all():
            if not analysis.is_successful():
                failed_analyses.append(analysis)
        
        return failed_analyses
    
    def delete_old_analyses(self, session_id, keep_latest=5):
        """Delete old analyses, keeping only the most recent ones"""
        analyses = self.find_by_session(session_id)
        if len(analyses) <= keep_latest:
            return 0
        
        # Sort by creation date and keep the latest ones
        analyses.sort(key=lambda a: a.created_at, reverse=True)
        analyses_to_delete = analyses[keep_latest:]
        
        count = 0
        for analysis in analyses_to_delete:
            analysis.delete()
            count += 1
        
        return count
    
    def get_analysis_performance_stats(self):
        """Get performance statistics for analyses"""
        from database import db
        from datetime import datetime, timedelta
        
        # Analyses in the last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_analyses = self.model.query.filter(self.model.created_at >= thirty_days_ago).all()
        
        successful_recent = sum(1 for a in recent_analyses if a.is_successful())
        failed_recent = len(recent_analyses) - successful_recent
        
        # Most common analysis types
        type_counts = db.session.query(
            AnalysisResult.analysis_type,
            db.func.count(AnalysisResult.id).label('count')
        ).filter(AnalysisResult.created_at >= thirty_days_ago)\
         .group_by(AnalysisResult.analysis_type)\
         .order_by(db.func.count(AnalysisResult.id).desc())\
         .all()
        
        return {
            'recent_analyses_count': len(recent_analyses),
            'successful_recent': successful_recent,
            'failed_recent': failed_recent,
            'success_rate': round(successful_recent / len(recent_analyses) * 100, 2) if recent_analyses else 0,
            'most_common_types': [(item.analysis_type, item.count) for item in type_counts[:5]]
        }
    
    def cleanup_session_analyses(self, session_id, user_id=None):
        """Clean up all analyses for a session with user permission check"""
        if user_id:
            from database.models import Session
            session = Session.query.get(session_id)
            if not session or session.user_id != user_id:
                return 0
        
        analyses = self.find_by_session(session_id)
        count = len(analyses)
        
        for analysis in analyses:
            analysis.delete()
        
        return count