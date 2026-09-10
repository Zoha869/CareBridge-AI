"""
Schema for the Doctor AI Assistant's chat endpoint.
"""

from typing import Optional
from pydantic import BaseModel


class DoctorChatIn(BaseModel):
    message: str
    patient_name_hint: Optional[str] = None


class DoctorChatOut(BaseModel):
    response: str