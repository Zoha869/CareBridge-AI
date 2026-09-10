# app/services/doctor_chat_service.py
"""
Doctor AI Assistant.

Grounded Q&A about the doctor's schedule/patients (existing behaviour),
plus natural-language actions once a patient is selected in the UI:
prescribing a medicine, giving a free-text instruction, or marking the
patient's appointment as visited/completed. Each action writes to the
same tables the Doctor/Patient dashboards already read from, so results
appear on both sides immediately.

Action detection is keyword-first (fast, reliable) with an LLM
classifier only as a fallback for instruction-vs-query - this avoids
depending on the LLM correctly returning JSON for every message.
"""

import re
from datetime import date
from sqlalchemy.orm import Session
from app.models.appointment import Appointment, AppointmentStatus
from app.models.patient import Patient
from app.models.user import User
from app.models.visit import Visit
from app.models.medication import Medication
from app.models.instruction import DoctorInstruction
from app.services.doctor_view_service import list_doctor_patients, get_patient_dossier
from app.services.summary_service import regenerate_summary
from app.services.llm_service import chat_completion, structured_completion

SYSTEM_PROMPT = """You are a hospital assistant helping a doctor quickly understand
their schedule and patients. Answer using ONLY the data below - never invent
appointments, patients, or medical details that aren't listed.

Today's appointments:
{todays_appointments}

Patients under this doctor's care:
{patient_list}
{patient_detail}
"""

# Catches dosage-style phrasing so a medicine message is recognized even
# if the classifier LLM call below fails or misfires.
DOSAGE_HINT_PATTERN = re.compile(
    r"\d+\s?(mg|mcg|ml|g)\b|tablet|capsule|syrup|injection|drops|"
    r"once daily|twice daily|thrice daily|three times daily|every \d+ hours",
    re.IGNORECASE,
)

# Catches "mark this patient as visited" style phrasing.
VISIT_HINT_PATTERN = re.compile(
    r"mark(ed)?\s+(as\s+)?visited|visit is done|seen the patient|appointment (is\s+)?(done|complete)",
    re.IGNORECASE,
)

# Catches common instruction-giving phrasing so it's recognized without
# depending on the LLM classifier to return the right JSON every time.
INSTRUCTION_HINT_PATTERN = re.compile(
    r"^(tell|advise|instruct|ask)\s+(him|her|them)\s+to\b|"
    r"\b(avoid|rest|refrain from|stay away from|don't|do not)\b.*\b(week|day|days|weeks|month|months)\b|"
    r"\bavoid\b|\brest\b",
    re.IGNORECASE,
)

ACTION_PROMPT = """A doctor is chatting about ONE selected patient. Their latest
message is NOT about medicine dosage and NOT about marking a visit done.
Decide if it's a free-text instruction for the patient, or just a question.

Return JSON only: {"action": "give_instruction" | "query"}
- "give_instruction": a non-medicine instruction for the patient (e.g. "avoid heavy exercise for 2 weeks", "rest for a week")
- "query": anything else (asking about the patient, schedule, etc.)
"""

MEDICINE_EXTRACT_PROMPT = """Extract the medicine the doctor is prescribing.
Return JSON only: {"name": "<medicine name>", "dosage": "<dosage>" or null, "instructions": "<how to take it>" or null}
"""

INSTRUCTION_EXTRACT_PROMPT = """Extract the doctor's instruction for the patient as one
clear sentence. Return JSON only: {"instruction_text": "<instruction>"}
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


def _patient_full_name(db: Session, patient_id) -> str:
    row = db.query(User.full_name).join(Patient, Patient.user_id == User.id).filter(Patient.id == patient_id).first()
    return row[0] if row else "the patient"


def _prescribe_medicine(db: Session, doctor_id, patient_id, message: str) -> str:
    extracted = structured_completion(MEDICINE_EXTRACT_PROMPT, message)
    name = extracted.get("name")
    if not name:
        return "I couldn't catch the medicine name - could you repeat it?"

    medication = Medication(
        patient_id=patient_id,
        doctor_id=doctor_id,
        name=name,
        dosage=extracted.get("dosage"),
        instructions=extracted.get("instructions"),
        prescribed_date=date.today(),
    )
    db.add(medication)
    db.commit()
    db.refresh(medication)
    regenerate_summary(db, patient_id)

    lines = [
        "🧾 Prescription saved",
        f"Patient: {_patient_full_name(db, patient_id)}",
        f"Medicine: {medication.name}",
    ]
    if medication.dosage:
        lines.append(f"Dosage: {medication.dosage}")
    if medication.instructions:
        lines.append(f"Instructions: {medication.instructions}")
    lines.append(f"Date: {medication.prescribed_date}")
    lines.append("Visible on the patient's dashboard and to their AI assistant now.")
    return "\n".join(lines)


def _give_instruction(db: Session, doctor_id, patient_id, message: str) -> str:
    extracted = structured_completion(INSTRUCTION_EXTRACT_PROMPT, message)
    text = extracted.get("instruction_text") or message

    instruction = DoctorInstruction(patient_id=patient_id, doctor_id=doctor_id, instruction_text=text)
    db.add(instruction)
    db.commit()
    regenerate_summary(db, patient_id)

    return (
        f"📋 Instruction saved for {_patient_full_name(db, patient_id)}:\n\"{text}\"\n"
        "Visible on their dashboard and to their AI assistant now."
    )


def _mark_visited(db: Session, doctor_id, patient_id) -> str:
    appointment = (
        db.query(Appointment)
        .filter(
            Appointment.doctor_id == doctor_id,
            Appointment.patient_id == patient_id,
            Appointment.status.in_([AppointmentStatus.CONFIRMED, AppointmentStatus.PENDING]),
        )
        .order_by(Appointment.appointment_date.desc())
        .first()
    )
    if appointment is None:
        return "I couldn't find an active appointment for this patient to mark as visited."

    appointment.status = AppointmentStatus.COMPLETED
    db.add(Visit(patient_id=patient_id, doctor_id=doctor_id, visit_date=appointment.appointment_date))
    db.commit()

    return f"Marked as visited - the appointment on {appointment.appointment_date} is now completed."


def answer_doctor_query(
    db: Session, doctor_id, message: str, patient_id=None, patient_name_hint: str | None = None
) -> str:
    """
    patient_id: the patient currently selected in the doctor's UI - when
    set, the message may be a write action (prescribe/instruct/mark
    visited) instead of a plain question.
    """
    if patient_id:
        if DOSAGE_HINT_PATTERN.search(message):
            return _prescribe_medicine(db, doctor_id, patient_id, message)
        if VISIT_HINT_PATTERN.search(message):
            return _mark_visited(db, doctor_id, patient_id)
        if INSTRUCTION_HINT_PATTERN.search(message):
            return _give_instruction(db, doctor_id, patient_id, message)

        action = structured_completion(ACTION_PROMPT, message).get("action", "query")
        if action == "give_instruction":
            return _give_instruction(db, doctor_id, patient_id, message)

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