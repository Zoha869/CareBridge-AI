"""
Pydantic schemas for appointment creation and responses.
"""

import uuid
from datetime import date, time, datetime
from typing import Optional
from pydantic import BaseModel


class AppointmentCreate(BaseModel):
    """Payload required to book a new appointment."""

    doctor_id: uuid.UUID
    appointment_date: date
    appointment_time: time
    reason: str


class AppointmentOut(BaseModel):
    """Public-facing representation of an appointment."""

    id: uuid.UUID
    patient_id: uuid.UUID
    doctor_id: uuid.UUID
    appointment_date: date
    appointment_time: time
    reason: str
    status: str
    created_at: datetime
    # Attached by the endpoint depending on viewpoint - a patient sees
    # the doctor's name, a doctor sees the patient's name.
    doctor_name: Optional[str] = None
    patient_name: Optional[str] = None

    class Config:
        from_attributes = True