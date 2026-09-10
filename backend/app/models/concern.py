"""
PatientConcern model.

Represents a specific health concern extracted from a patient's
conversation (Phase 4: Patient Intelligence will populate this
automatically; Phase 1 only defines the schema).
"""

import uuid
import enum
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class ConcernSeverity(str, enum.Enum):
    """Triage severity level assigned to a concern."""

    LOW = "low"
    MODERATE = "moderate"
    URGENT = "urgent"


class ConcernStatus(str, enum.Enum):
    """Whether a concern is still open or has been addressed."""

    OPEN = "open"
    REVIEWED = "reviewed"
    RESOLVED = "resolved"


class PatientConcern(Base):
    """A discrete health concern raised by or extracted from a patient."""

    __tablename__ = "patient_concerns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(Enum(ConcernSeverity), nullable=False, default=ConcernSeverity.LOW)
    status = Column(Enum(ConcernStatus), nullable=False, default=ConcernStatus.OPEN)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient", back_populates="concerns")
