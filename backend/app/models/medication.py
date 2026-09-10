"""
Medication model.

Stores medications prescribed to a patient, used by the Patient AI
Assistant to answer questions like "what are the instructions for my
prescribed medicine?".
"""

import uuid
from sqlalchemy import Column, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class Medication(Base):
    """A medication prescribed to a patient."""

    __tablename__ = "medications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id"), nullable=True)
    name = Column(String, nullable=False)
    dosage = Column(String, nullable=True)
    instructions = Column(Text, nullable=True)
    prescribed_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient", back_populates="medications")
