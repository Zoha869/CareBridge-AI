"""
Classifies an incoming patient message into one workflow intent,
used by the LangGraph router to decide which node handles it.
"""

import re
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


# Runs independently of detect_intent/booking-state, so a red-flag symptom
# typed as an appointment "reason" mid-booking still gets caught - the main
# intent classifier is told to keep booking flow going even for messages
# that "look unrelated", which was silently swallowing urgent symptoms.
# Regex safety net checked FIRST - same "keyword-first, LLM as fallback"
# pattern already used on the doctor side (doctor_chat_service.py), because
# a small model can be inconsistent judging a calmly-phrased red flag like
# "chest pain on and off for two days, worse on stairs" as urgent.
RED_FLAG_PATTERN = re.compile(
    r"chest pain|chest tight|difficulty breathing|can'?t breathe|shortness of breath|"
    r"severe bleeding|heavy bleeding|unconscious|passed out|fainted|"
    r"\bstroke\b|slurred speech|numbness on one side|face drooping|"
    r"suicidal|kill myself|end my life|"
    r"worse (when|with|on) (climbing|exertion|exercise|activity|stairs)",
    re.IGNORECASE,
)

URGENCY_PROMPT = """You are a medical safety screener. Look ONLY at the patient's
LATEST message below and judge whether it describes symptoms that could be a
medical emergency needing immediate/same-day in-person care (e.g. chest pain,
difficulty breathing, severe bleeding, stroke signs, loss of consciousness,
suicidal ideation). Ignore whether they're also booking an appointment, asking
a question, etc. - judge the symptom content only, even if it's described
calmly or matter-of-factly. Any chest pain - especially if triggered or
worsened by exertion (e.g. climbing stairs) or persisting for more than a
day - counts as urgent even without dramatic wording.

Return JSON only: {"urgent": true | false}"""


def detect_urgency(message: str) -> bool:
    if RED_FLAG_PATTERN.search(message):
        return True
    result = structured_completion(URGENCY_PROMPT, message)
    return bool(result.get("urgent", False))