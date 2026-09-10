"""
Pydantic schemas for conversation and message endpoints.
"""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class MessageIn(BaseModel):
    """Payload sent by the patient when chatting with the AI assistant."""

    conversation_id: Optional[uuid.UUID] = None
    content: str


class MessageOut(BaseModel):
    """A single message returned to the frontend."""

    id: uuid.UUID
    conversation_id: uuid.UUID
    sender_role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True