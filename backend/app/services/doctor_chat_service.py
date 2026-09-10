"""
Doctor AI Assistant - lets a doctor ask about their schedule and
patients in natural language. Simpler than the patient assistant
(no booking/cancelling), so this is a single grounded LLM call
rather than a multi-branch LangGraph, per the proposal's Doctor AI
Chat feature.
"""

from datetime import date
from sqlalchemy.orm import Session
from app.models.appointment import Appointment, AppointmentStatus
from app.models.doctor import Doctor
from app.services.doctor_view_service import list_doctor_patients, get_patient_dossier
from app.services.llm_service import chat_completion

SYSTEM_PROMPT = """You are a hospital assistant helping a doctor quickly understand
their schedule and patients. Answer using ONLY the data below - never invent
appointments, patients, or medical details that aren't listed.

Today's appointments:
{todays_appointments}

Patients under this doctor's care:
{patient_list}
{patient_detail}
"""


def _format_todays_appointments(db: Session, doctor_id) -> str:
    appointments = (
        db.query(Appointment)
        .filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == date.today(),
            Appointment.status != AppointmentStatus.CANCELLED,
        )
        .all()
    )
    if not appointments:
        return "None today."
    return "\n".join(f"- {a.appointment_time}: {a.reason} (status: {a.status.value})" for a in appointments)


def _format_patient_list(db: Session, doctor_id) -> str:
    patients = list_doctor_patients(db, doctor_id)
    if not patients:
        return "None yet."
    return "\n".join(f"- {p['full_name']} (last seen {p['last_appointment_date']})" for p in patients)


def answer_doctor_query(db: Session, doctor_id, message: str, patient_name_hint: str | None = None) -> str:
    """
    patient_name_hint: if the caller already knows which patient the
    doctor is asking about (e.g. selected in the UI), their full
    dossier is included for a detailed answer.
    """
    patient_detail = ""
    if patient_name_hint:
        patients = list_doctor_patients(db, doctor_id)
        match = next((p for p in patients if patient_name_hint.lower() in p["full_name"].lower()), None)
        if match:
            dossier = get_patient_dossier(db, match["patient_id"])
            patient_detail = f"\nDetail for {dossier['full_name']}:\nSummary: {dossier['summary'] or 'No summary yet.'}"

    system_prompt = SYSTEM_PROMPT.format(
        todays_appointments=_format_todays_appointments(db, doctor_id),
        patient_list=_format_patient_list(db, doctor_id),
        patient_detail=patient_detail,
    )
    return chat_completion(system_prompt, [{"role": "user", "content": message}])