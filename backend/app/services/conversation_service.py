"""
DB operations for conversations and messages, used by the patient
assistant's LangGraph workflow.
"""

from sqlalchemy.orm import Session
from app.models.conversation import Conversation
from app.models.message import Message, SenderRole

HISTORY_LIMIT = 15  # only recent messages go to the LLM, not full history
DISPLAY_LIMIT = 100  # how much history the frontend loads on page open


def get_or_create_conversation(db: Session, patient_id) -> Conversation:
    conversation = (
        db.query(Conversation)
        .filter(Conversation.patient_id == patient_id, Conversation.ended_at.is_(None))
        .order_by(Conversation.started_at.desc())
        .first()
    )
    if conversation:
        return conversation

    conversation = Conversation(patient_id=patient_id)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def save_message(db: Session, conversation_id, sender_role: SenderRole, content: str) -> Message:
    message = Message(conversation_id=conversation_id, sender_role=sender_role, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_recent_messages(db: Session, conversation_id) -> list[dict]:
    """LLM-facing: role/content dicts only, capped small to control token usage."""
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(HISTORY_LIMIT)
        .all()
    )
    messages.reverse()
    return [
        {"role": "user" if m.sender_role == SenderRole.PATIENT else "assistant", "content": m.content}
        for m in messages
    ]


def get_display_messages(db: Session, conversation_id) -> list[Message]:
    """Frontend-facing: full Message rows, for restoring the chat on page load."""
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .limit(DISPLAY_LIMIT)
        .all()
    )
    return messages