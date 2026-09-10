"""
DoctorInstruction model.

Stores explicit instructions a doctor has given a patient, separate
from medications (e.g. "avoid heavy exercise for two weeks"). Used by
the Patient AI Assistant for "what instructions did the doctor give
me?" style questions.
"""

import uuid
from sqlalchemy import Column, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.database import Base


class DoctorInstruction(Base):
    """A free-text instruction given by a doctor to a patient."""

    __tablename__ = "doctor_instructions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id"), nullable=False)
    instruction_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
