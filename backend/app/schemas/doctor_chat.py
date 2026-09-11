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


class PatientOption(BaseModel):
    """One choice offered to the doctor when a patient still needs picking."""

    patient_id: uuid.UUID
    full_name: str


class DoctorChatOut(BaseModel):
    response: str

    # Set when the doctor's message was clearly a patient-directed action
    # (prescribe / instruct / mark visited) but no patient could be
    # resolved from the UI selection or the wording itself - the frontend
    # should render patient_options as a picker instead of guessing.
    needs_patient_selection: bool = False
    patient_options: list[PatientOption] = []
    # The doctor's original message, echoed back so the frontend can
    # resend it together with the patient the doctor picks.
    pending_message: Optional[str] = None

    # Whenever a patient WAS resolved (via UI selection, or by name from
    # the message/picker), it's returned here so the frontend can sync
    # its own "selected patient" state - this is what lets the doctor
    # keep talking about the same patient without re-selecting every turn.
    resolved_patient_id: Optional[uuid.UUID] = None
    resolved_patient_name: Optional[str] = None