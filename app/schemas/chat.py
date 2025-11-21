# app/schemas/chat.py
from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional
import uuid
import json

class MessageCreate(BaseModel):
    receiver_identifier: str  # email or full name
    content: str
    message_type: str = "text"

    @validator('content')
    def validate_content_length(cls, v):
        words = v.strip().split()
        if len(words) > 200:
            raise ValueError('Message cannot exceed 200 words')
        if len(words) == 0:
            raise ValueError('Message cannot be empty')
        return v

    @validator('message_type')
    def validate_message_type(cls, v):
        if v not in ['text', 'image', 'file']:
            raise ValueError('Invalid message type')
        return v

class MessageResponse(BaseModel):
    id: int
    sender_id: uuid.UUID
    receiver_id: uuid.UUID
    content: str
    message_type: str
    timestamp: datetime
    is_read: bool

    class Config:
        from_attributes = True
        json_encoders = {
            uuid.UUID: lambda v: str(v),  # Convert UUID to string
            datetime: lambda v: v.isoformat()  # Convert datetime to ISO string
        }

    def dict(self, **kwargs):
        # Override to ensure proper serialization
        data = super().dict(**kwargs)
        # Convert UUID and datetime for JSON compatibility
        data['sender_id'] = str(data['sender_id'])
        data['receiver_id'] = str(data['receiver_id'])
        data['timestamp'] = data['timestamp'].isoformat()
        return data