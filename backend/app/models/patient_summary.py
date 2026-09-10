"""
PatientSummary model.

Holds the most recent AI-generated summary of a patient's context
(recent concerns, visits, medications). Regenerated whenever a new
concern is logged. Read by the Doctor Assistant (Phase 5) so a doctor
doesn't have to read the raw conversation.
"""

import uuid
from sqlalchemy import Column, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.database import Base


class PatientSummary(Base):
    """The single current summary for a patient (one row per patient)."""

    __tablename__ = "patient_summaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), unique=True, nullable=False)
    summary_text = Column(Text, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())