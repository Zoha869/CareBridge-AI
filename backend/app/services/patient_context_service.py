"""
Retrieves a patient's stored medical context (visits, medications,
instructions, concerns) from the database. Used to ground the
assistant's answers to "when was my last visit" style questions in
real data instead of letting the LLM guess.
"""

from sqlalchemy.orm import Session
from app.models.appointment import Appointment
from app.models.visit import Visit
from app.models.medication import Medication
from app.models.instruction import DoctorInstruction
from app.models.concern import PatientConcern

RECENT_LIMIT = 5


def get_recent_appointments(db: Session, patient_id) -> list[Appointment]:
    return (
        db.query(Appointment)
        .filter(Appointment.patient_id == patient_id)
        .order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc())
        .limit(RECENT_LIMIT)
        .all()
    )


def get_recent_visits(db: Session, patient_id) -> list[Visit]:
    return (
        db.query(Visit)
        .filter(Visit.patient_id == patient_id)
        .order_by(Visit.visit_date.desc())
        .limit(RECENT_LIMIT)
        .all()
    )


def get_medications(db: Session, patient_id) -> list[Medication]:
    return (
        db.query(Medication)
        .filter(Medication.patient_id == patient_id)
        .order_by(Medication.prescribed_date.desc())
        .limit(RECENT_LIMIT)
        .all()
    )


def get_instructions(db: Session, patient_id) -> list[DoctorInstruction]:
    return (
        db.query(DoctorInstruction)
        .filter(DoctorInstruction.patient_id == patient_id)
        .order_by(DoctorInstruction.created_at.desc())
        .limit(RECENT_LIMIT)
        .all()
    )


def get_open_concerns(db: Session, patient_id) -> list[PatientConcern]:
    return (
        db.query(PatientConcern)
        .filter(PatientConcern.patient_id == patient_id, PatientConcern.status == "open")
        .order_by(PatientConcern.created_at.desc())
        .all()
    )


def build_context_text(db: Session, patient_id) -> str:
    """Formats everything into plain text the LLM can ground an answer in."""
    appointments = get_recent_appointments(db, patient_id)
    visits = get_recent_visits(db, patient_id)
    medications = get_medications(db, patient_id)
    instructions = get_instructions(db, patient_id)
    concerns = get_open_concerns(db, patient_id)

    parts = []

    if appointments:
        parts.append(
            "Appointments:\n"
            + "\n".join(
                f"- {a.appointment_date} at {a.appointment_time}: {a.reason} (status: {a.status.value})"
                for a in appointments
            )
        )
    else:
        parts.append("Appointments: none on record.")

    if visits:
        parts.append("Recent visits:\n" + "\n".join(f"- {v.visit_date}: {v.notes or 'no notes recorded'}" for v in visits))
    else:
        parts.append("Recent visits: none on record.")

    if medications:
        parts.append(
            "Medications:\n"
            + "\n".join(f"- {m.name} ({m.dosage or 'dosage not specified'}): {m.instructions or ''}" for m in medications)
        )
    else:
        parts.append("Medications: none on record.")

    if instructions:
        parts.append("Doctor instructions:\n" + "\n".join(f"- {i.instruction_text}" for i in instructions))
    else:
        parts.append("Doctor instructions: none on record.")

    if concerns:
        parts.append("Open concerns:\n" + "\n".join(f"- {c.description} (severity: {c.severity.value})" for c in concerns))
    else:
        parts.append("Open concerns: none.")

    return "\n\n".join(parts)