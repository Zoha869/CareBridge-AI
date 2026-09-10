"""
Schemas for the Doctor Dashboard: the patient list and the full
patient "dossier" view described in the proposal's Section 9
(Overview -> Current Concern -> Visits -> Medications -> Summary).
"""

import uuid
from datetime import date, time, datetime
from typing import Optional
from pydantic import BaseModel


class PatientBrief(BaseModel):
    """One row in the doctor's patient list."""

    patient_id: uuid.UUID
    full_name: str
    last_appointment_date: Optional[date] = None
    open_concern_count: int = 0
    top_severity: Optional[str] = None
    has_summary: bool = False


class VisitBrief(BaseModel):
    visit_date: date
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class MedicationBrief(BaseModel):
    name: str
    dosage: Optional[str] = None
    instructions: Optional[str] = None
    prescribed_date: Optional[date] = None

    class Config:
        from_attributes = True


class InstructionBrief(BaseModel):
    instruction_text: str
    created_at: datetime

    class Config:
        from_attributes = True


class ConcernBrief(BaseModel):
    description: str
    severity: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class AppointmentBrief(BaseModel):
    appointment_date: date
    appointment_time: time
    reason: str
    status: str

    class Config:
        from_attributes = True


class PatientDossier(BaseModel):
    """Full patient record a doctor sees when opening a patient."""

    patient_id: uuid.UUID
    full_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    phone_number: Optional[str] = None
    summary: Optional[str] = None
    open_concerns: list[ConcernBrief] = []
    recent_visits: list[VisitBrief] = []
    medications: list[MedicationBrief] = []
    instructions: list[InstructionBrief] = []
    appointments: list[AppointmentBrief] = []