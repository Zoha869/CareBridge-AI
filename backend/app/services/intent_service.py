"""
Classifies an incoming patient message into one workflow intent,
used by the LangGraph router to decide which node handles it.
"""

from app.services.llm_service import structured_completion

INTENT_PROMPT = """You classify the patient's LATEST message into exactly one intent,
using the conversation so far for context. If the conversation is already in the
middle of booking an appointment (doctor/date/time/reason being collected) and the
latest message is answering that (a name, a date, a time, a reason), classify it
as "appointment" - not general_question - even if the message alone looks unrelated.

Return JSON only: {"intent": "<value>"}
Allowed values:
- "general_question": general medical/hospital info question, unrelated to booking
- "patient_history": asking about past visits, instructions, or medications
- "appointment": wants to book/reschedule/cancel, OR is continuing an in-progress booking
- "new_concern": reporting a new symptom or health issue, unrelated to booking
- "urgent": message suggests a medical emergency
"""


def detect_intent(message: str, history: list[dict]) -> str:
    conversation_text = "\n".join(f"{m['role']}: {m['content']}" for m in history)
    conversation_text += f"\nuser: {message}"
    result = structured_completion(INTENT_PROMPT, conversation_text)
    return result.get("intent", "general_question")