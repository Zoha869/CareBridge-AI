"""
Pydantic schemas for patient profile data.
"""

import uuid
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class PatientProfileUpdate(BaseModel):
    """Fields a patient can update on their own profile."""

    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None


class PatientOut(BaseModel):
    """Public-facing representation of a patient profile."""

    id: uuid.UUID
    user_id: uuid.UUID
    full_name: str
    date_of_birth: Optional[date]
    gender: Optional[str]
    phone_number: Optional[str]
    address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True