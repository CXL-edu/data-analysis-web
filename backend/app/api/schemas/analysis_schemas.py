"""
Analysis API schemas
"""
from marshmallow import Schema, fields, validate


class AnalysisRequestSchema(Schema):
    """Schema for analysis requests"""
    analysis_type = fields.Str(
        required=True,
        validate=validate.OneOf([
            'descriptive_stats',
            'correlation_analysis',
            'data_profiling',
            'visualization',
            'anomaly_detection',
            'time_series'
        ])
    )
    file_ids = fields.List(fields.Int(), load_default=[])
    parameters = fields.Dict(load_default={})