"""
Conversation model.

Represents a single conversation session between a patient and the
Patient AI Assistant. Individual chat turns are stored separately in
the "messages" table, linked by conversation_id.
"""

import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class Conversation(Base):
    """A chat session belonging to one patient."""

    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    channel = Column(String, nullable=False, default="chat")  # "chat" or "voice"
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)

    messages = relationship("Message", back_populates="conversation")
