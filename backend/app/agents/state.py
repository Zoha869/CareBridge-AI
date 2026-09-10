"""
Shared state passed between every node in the patient assistant graph.
"""

from typing import TypedDict, Any


class PatientState(TypedDict):
    db: Any               # SQLAlchemy session for this request
    patient_id: Any        # UUID of the Patient row (not the Supabase user id)
    conversation_id: Any
    message: str
    history: list[dict]
    intent: str
    response: str