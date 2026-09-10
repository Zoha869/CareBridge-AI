# app/schemas/doctor_chat.py
"""
Schema for the Doctor AI Assistant's chat endpoint.
"""

import uuid
from typing import Optional
from pydantic import BaseModel


class DoctorChatIn(BaseModel):
    message: str
    patient_id: Optional[uuid.UUID] = None  # patient selected in the UI - enables prescribe/instruct/mark-visited actions
    patient_name_hint: Optional[str] = None


class DoctorChatOut(BaseModel):
    response: str