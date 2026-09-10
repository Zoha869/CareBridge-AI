"""
Doctor model.

Stores professional-profile information specific to doctors. Linked
one-to-one with the "users" table via user_id.
"""

import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class Doctor(Base):
    """Doctor profile record, one per doctor user."""

    __tablename__ = "doctors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    specialization = Column(String, nullable=True)
    license_number = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships to other tables that reference this doctor.
    appointments = relationship("Appointment", back_populates="doctor")
    visits = relationship("Visit", back_populates="doctor")
