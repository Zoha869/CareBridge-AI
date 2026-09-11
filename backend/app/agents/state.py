"""
Shared state passed between every node in the patient assistant graph.
"""

from typing import TypedDict, Any


class PatientState(TypedDict, total=False):
    db: Any               # SQLAlchemy session for this request
    patient_id: Any        # UUID of the Patient row (not the Supabase user id)
    conversation_id: Any
    message: str
    history: list[dict]
    intent: str
    response: str
    urgent_notice: str     # set when urgent but booking is left to continue - prepended to the booking response
    urgent_logged: bool    # true once safety_check_node has already saved the urgent concern, so booking doesn't duplicate it