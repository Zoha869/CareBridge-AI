"""
Extracts a structured concern (description + severity) from what the
patient just said, and saves it. This is the "Patient Information
Extraction" and "New Concern Reporting" features from the proposal.
"""

from sqlalchemy.orm import Session
from app.models.concern import PatientConcern, ConcernSeverity
from app.services.llm_service import structured_completion

EXTRACT_PROMPT = """The patient just reported a new health concern. Summarize it in
one clear clinical sentence, and judge its severity.

Return JSON only:
{"description": "<one-sentence summary>", "severity": "low" | "moderate" | "urgent"}

Severity guide:
- "urgent": suggests a medical emergency (already screened separately, but flag if borderline)
- "moderate": persistent, worsening, or concerning but not an emergency
- "low": mild, routine, or short-lived
"""


def extract_and_save_concern(db: Session, patient_id, message: str, history: list[dict]) -> PatientConcern:
    conversation_text = "\n".join(f"{m['role']}: {m['content']}" for m in history)
    conversation_text += f"\nuser: {message}"

    extracted = structured_completion(EXTRACT_PROMPT, conversation_text)

    concern = PatientConcern(
        patient_id=patient_id,
        description=extracted.get("description", message),
        severity=ConcernSeverity(extracted.get("severity", "low")),
    )
    db.add(concern)
    db.commit()
    db.refresh(concern)
    return concern