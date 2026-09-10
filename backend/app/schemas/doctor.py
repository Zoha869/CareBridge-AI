"""
Pydantic schemas for doctor profile data.
"""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DoctorProfileUpdate(BaseModel):
    """Fields a doctor can update on their own profile."""

    specialization: Optional[str] = None
    license_number: Optional[str] = None
    phone_number: Optional[str] = None


class DoctorOut(BaseModel):
    """Public-facing representation of a doctor profile."""

    id: uuid.UUID
    user_id: uuid.UUID
    full_name: str
    specialization: Optional[str]
    license_number: Optional[str]
    phone_number: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True