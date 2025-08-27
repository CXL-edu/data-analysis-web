"""
Session management API schemas
"""
from marshmallow import Schema, fields, validate


class CreateSessionSchema(Schema):
    """Schema for creating a new session"""
    title = fields.Str(validate=validate.Length(min=1, max=200), allow_none=True, load_default=None)


class UpdateSessionSchema(Schema):
    """Schema for updating session details"""
    title = fields.Str(validate=validate.Length(min=1, max=200), required=False)