"""
Analysis result model for storing data analysis results
"""
from sqlalchemy import Column, String, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel


class AnalysisResult(BaseModel):
    """Model for storing data analysis results"""
    
    __tablename__ = 'analysis_results'
    
    # Foreign key to session
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False, index=True)
    
    # Analysis information
    analysis_type = Column(String(50), nullable=False, index=True)
    results = Column(JSON, nullable=False)
    
    # Relationships
    session = relationship('Session', back_populates='analysis_results')
    
    def __init__(self, session_id, analysis_type, results):
        """Initialize analysis result"""
        self.session_id = session_id
        self.analysis_type = analysis_type
        self.results = results
    
    def update_results(self, new_results):
        """Update analysis results"""
        self.results = new_results
        self.save()
    
    def get_result_summary(self):
        """Get a summary of the analysis results"""
        if not self.results:
            return "No results available"
        
        summary = {
            'analysis_type': self.analysis_type,
            'result_keys': list(self.results.keys()) if isinstance(self.results, dict) else [],
            'created_at': self.created_at.isoformat()
        }
        
        # Add type-specific summaries
        if self.analysis_type == 'summary':
            summary['basic_info'] = self.results.get('basic_info', {})
        elif self.analysis_type == 'correlation':
            summary['strong_correlations'] = len(self.results.get('strong_correlations', []))
        elif self.analysis_type == 'missing_values':
            summary['missing_columns'] = len(self.results.get('missing_by_column', []))
        
        return summary
    
    def is_successful(self):
        """Check if analysis was successful (no error in results)"""
        return 'error' not in self.results
    
    def get_error_message(self):
        """Get error message if analysis failed"""
        return self.results.get('error', None)
    
    @classmethod
    def find_by_session(cls, session_id):
        """Find all analysis results for a session"""
        return cls.query.filter_by(session_id=session_id)\
                        .order_by(cls.created_at.desc())\
                        .all()
    
    @classmethod
    def find_by_type(cls, session_id, analysis_type):
        """Find analysis results by type for a session"""
        return cls.query.filter_by(session_id=session_id, analysis_type=analysis_type)\
                        .order_by(cls.created_at.desc())\
                        .first()
    
    @classmethod
    def find_latest_by_session(cls, session_id):
        """Find the most recent analysis result for a session"""
        return cls.query.filter_by(session_id=session_id)\
                        .order_by(cls.created_at.desc())\
                        .first()
    
    @classmethod
    def get_analysis_types_for_session(cls, session_id):
        """Get all analysis types that have been run for a session"""
        results = cls.query.filter_by(session_id=session_id)\
                          .with_entities(cls.analysis_type)\
                          .distinct()\
                          .all()
        return [result[0] for result in results]
    
    @classmethod
    def count_by_session(cls, session_id):
        """Count total analysis results for a session"""
        return cls.query.filter_by(session_id=session_id).count()
    
    def to_dict(self):
        """Convert analysis result to dictionary"""
        result = super().to_dict()
        result.update({
            'is_successful': self.is_successful(),
            'summary': self.get_result_summary()
        })
        return result
    
    def __repr__(self):
        return f'<AnalysisResult {self.analysis_type} for Session {self.session_id}>'