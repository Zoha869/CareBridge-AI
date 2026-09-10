"""
Generates and stores the patient's current summary - the "Summary
Generation" feature, and what api/v1/doctors.py (Phase 5) will read
instead of a raw conversation log.
"""

from sqlalchemy.orm import Session
from app.models.patient_summary import PatientSummary
from app.services.patient_context_service import build_context_text
from app.services.llm_service import chat_completion

SUMMARY_PROMPT = """You write a short clinical-style summary of a patient for a
doctor who has 10 seconds to read it before the appointment. 3-4 sentences,
plain language, no headers. Mention the most relevant open concern first."""


def regenerate_summary(db: Session, patient_id) -> PatientSummary:
    context_text = build_context_text(db, patient_id)
    summary_text = chat_completion(SUMMARY_PROMPT, [{"role": "user", "content": context_text}])

    summary = db.query(PatientSummary).filter(PatientSummary.patient_id == patient_id).first()
    if summary:
        summary.summary_text = summary_text
    else:
        summary = PatientSummary(patient_id=patient_id, summary_text=summary_text)
        db.add(summary)

    db.commit()
    db.refresh(summary)
    return summary