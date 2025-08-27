"""
Chat API schemas
"""
from marshmallow import Schema, fields, validate


class SendMessageSchema(Schema):
    """Schema for sending a message"""
    message = fields.Str(required=True, validate=validate.Length(min=1, max=10000))