# app/api/v1/conversations.py
"""
Conversation endpoints: /api/v1/conversations/*

The patient's single chat entry point. Every message is routed through
the LangGraph patient assistant, which decides how to respond and
whether to take an action (like booking an appointment).
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.deps import require_patient
from app.core.security import CurrentUser
from app.models.patient import Patient
from app.models.message import SenderRole
from app.schemas.conversation import MessageIn, MessageOut
from app.services.conversation_service import get_or_create_conversation, save_message, get_display_messages
from app.agents.graph import patient_graph

router = APIRouter(prefix="/conversations", tags=["Conversations"])


def _get_own_patient(db: Session, user: CurrentUser) -> Patient:
    patient = db.query(Patient).filter(Patient.user_id == user.supabase_id).first()
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found.")
    return patient


@router.get("/history", response_model=List[MessageOut])
def get_conversation_history(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_patient),
):
    """
    Restores the patient's ongoing conversation on page load, so
    refreshing the dashboard doesn't lose the chat.
    """
    patient = _get_own_patient(db, user)
    conversation = get_or_create_conversation(db, patient.id)
    return get_display_messages(db, conversation.id)


@router.post("/messages", response_model=MessageOut)
def send_message(
    payload: MessageIn,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_patient),
):
    """Sends a patient message to the AI assistant and returns its reply."""
    patient = _get_own_patient(db, user)

    if payload.conversation_id:
        conversation_id = payload.conversation_id
    else:
        conversation_id = get_or_create_conversation(db, patient.id).id

    save_message(db, conversation_id, SenderRole.PATIENT, payload.content)

    try:
        result = patient_graph.invoke(
            {
                "db": db,
                "patient_id": patient.id,
                "conversation_id": conversation_id,
                "message": payload.content,
            }
        )
        response_text = result["response"]
    except Exception:
        # Fallback instead of a raw 500 - the patient always gets a reply,
        # this was previously causing the "assistant didn't respond" issue.
        response_text = "Sorry, I couldn't process that just now. Could you try rephrasing, or try again in a moment?"

    ai_message = save_message(db, conversation_id, SenderRole.AI, response_text)
    return ai_message