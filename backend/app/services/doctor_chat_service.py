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


def _find_patient_by_name(patients: list[dict], text: str | None) -> dict | None:
    """Matches a patient's full name inside free text (case-insensitive).

    Only returns a match when exactly one patient's name appears in the
    text - an ambiguous or empty match means "let the picker handle it"
    rather than guessing wrong.
    """
    if not text:
        return None
    text_lower = text.lower()
    matches = [p for p in patients if p["full_name"].lower() in text_lower]
    return matches[0] if len(matches) == 1 else None


def _resolve_patient(db: Session, doctor_id, patients: list[dict], patient_id, patient_name_hint: str | None, message: str) -> dict | None:
    """Figures out which patient (if any) this message is about.

    Priority: an explicit patient_id from the UI selection wins outright;
    otherwise try to match a name mentioned in the hint or the doctor's
    own message text against this doctor's patient list.
    """
    if patient_id:
        match = next((p for p in patients if str(p["patient_id"]) == str(patient_id)), None)
        return match or {"patient_id": patient_id, "full_name": patient_name_hint or "the patient"}

    return _find_patient_by_name(patients, patient_name_hint) or _find_patient_by_name(patients, message)


def _result(
    response: str,
    resolved: dict | None = None,
    needs_selection: bool = False,
    patient_options: list[dict] | None = None,
    pending_message: str | None = None,
) -> dict:
    """Standard shape returned to the API layer / DoctorChatOut."""
    return {
        "response": response,
        "needs_patient_selection": needs_selection,
        "patient_options": patient_options or [],
        "pending_message": pending_message,
        "resolved_patient_id": resolved["patient_id"] if resolved else None,
        "resolved_patient_name": resolved["full_name"] if resolved else None,
    }


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
) -> dict:
    """
    patient_id: the patient currently selected in the doctor's UI - when
    set, the message may be a write action (prescribe/instruct/mark
    visited) instead of a plain question.

    If no patient_id is given, this now also tries to resolve one from
    the doctor's own wording (e.g. "give Zoha-008 Panadol 500mg..." in a
    single message). If the message is clearly a patient-directed action
    (dosage / instruction / mark-visited) and still no patient can be
    resolved, it returns a picker instead of silently falling back to
    generic chat and asking the doctor to repeat themselves.
    """
    patients = list_doctor_patients(db, doctor_id)
    resolved = _resolve_patient(db, doctor_id, patients, patient_id, patient_name_hint, message)
    resolved_patient_id = resolved["patient_id"] if resolved else None

    is_action_intent = bool(
        DOSAGE_HINT_PATTERN.search(message)
        or VISIT_HINT_PATTERN.search(message)
        or INSTRUCTION_HINT_PATTERN.search(message)
    )

    if resolved_patient_id is None and is_action_intent:
        return _result(
            "Which patient is this for? Pick one and I'll apply it right away.",
            needs_selection=True,
            patient_options=[{"patient_id": p["patient_id"], "full_name": p["full_name"]} for p in patients],
            pending_message=message,
        )

    if resolved_patient_id:
        if DOSAGE_HINT_PATTERN.search(message):
            return _result(_prescribe_medicine(db, doctor_id, resolved_patient_id, message), resolved)
        if VISIT_HINT_PATTERN.search(message):
            return _result(_mark_visited(db, doctor_id, resolved_patient_id), resolved)
        if INSTRUCTION_HINT_PATTERN.search(message):
            return _result(_give_instruction(db, doctor_id, resolved_patient_id, message), resolved)

        action = structured_completion(ACTION_PROMPT, message).get("action", "query")
        if action == "give_instruction":
            return _result(_give_instruction(db, doctor_id, resolved_patient_id, message), resolved)

    patient_detail = ""
    if resolved:
        dossier = get_patient_dossier(db, resolved["patient_id"])
        patient_detail = f"\nDetail for {dossier['full_name']}:\nSummary: {dossier['summary'] or 'No summary yet.'}"

    system_prompt = SYSTEM_PROMPT.format(
        todays_appointments=_format_todays_appointments(db, doctor_id),
        patient_list=_format_patient_list(db, doctor_id),
        patient_detail=patient_detail,
    )
    text = chat_completion(system_prompt, [{"role": "user", "content": message}])
    return _result(text, resolved)