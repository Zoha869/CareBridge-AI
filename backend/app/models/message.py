"""
Message model.

Represents a single message within a conversation — from the patient,
the AI, or (in escalation cases) the doctor.
"""

import uuid
import enum
from sqlalchemy import Column, Text, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class SenderRole(str, enum.Enum):
    """Who authored a given message."""

    PATIENT = "patient"
    AI = "ai"
    DOCTOR = "doctor"


class Message(Base):
    """A single turn within a conversation."""

    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    sender_role = Column(Enum(SenderRole), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")
