# app/models/document.py
"""
Document model — a patient-uploaded file (Tab 13 of the CareBridge
Clinical Knowledge Base: lab reports, prescriptions, imaging, discharge
summaries, etc.). The actual file bytes live in Supabase Storage; this
row is the metadata + extracted-text record, and its extracted text is
also what gets embedded into Qdrant for RAG (see document_service.py).
"""

import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id"), nullable=True)  # set only when a doctor uploaded this

    document_type = Column(String, nullable=False, default="other")  # lab_report/prescription/imaging/discharge_summary/other
    original_filename = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)  # path within the Supabase Storage bucket
    extracted_text = Column(Text, nullable=True)  # null if extraction failed
    visibility = Column(String, nullable=False, default="PRIVATE")  # PRIVATE/SHARED/CARE_TEAM

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient")