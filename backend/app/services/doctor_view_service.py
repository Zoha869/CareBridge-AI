"""
Assembles the Doctor Dashboard's patient list and per-patient
dossier. Enforces the proposal's security rule: "Doctor access
limited to assigned/authorized patients" - a doctor may only view
patients they have at least one appointment with.
"""

from sqlalchemy.orm import Session
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.user import User
from app.models.appointment import Appointment, AppointmentStatus
from app.models.patient_summary import PatientSummary
from app.services.patient_context_service import (
    get_recent_visits,
    get_medications,
    get_instructions,
    get_open_concerns,
)

_SEVERITY_RANK = {"low": 0, "moderate": 1, "urgent": 2}


def doctor_has_access(db: Session, doctor_id, patient_id) -> bool:
    """A doctor may view a patient only if they share an appointment."""
    appointment = (
        db.query(Appointment)
        .filter(Appointment.doctor_id == doctor_id, Appointment.patient_id == patient_id)
        .first()
    )
    return appointment is not None


def list_doctor_patients(db: Session, doctor_id) -> list[dict]:
    """
    Every distinct patient this doctor has an appointment with, most
    recent first - with enough concern/summary info for the dashboard
    to show at-a-glance status without fetching each full dossier.
    """
    rows = (
        db.query(Patient.id, User.full_name, Appointment.appointment_date)
        .join(User, Patient.user_id == User.id)
        .join(Appointment, Appointment.patient_id == Patient.id)
        .filter(Appointment.doctor_id == doctor_id, Appointment.status != AppointmentStatus.CANCELLED)
        .order_by(Appointment.appointment_date.desc())
        .all()
    )

    seen = {}
    for patient_id, full_name, appt_date in rows:
        if patient_id not in seen:
            seen[patient_id] = {
                "patient_id": patient_id,
                "full_name": full_name,
                "last_appointment_date": appt_date,
            }

    for patient_id, entry in seen.items():
        concerns = get_open_concerns(db, patient_id)
        entry["open_concern_count"] = len(concerns)
        entry["top_severity"] = (
            max(concerns, key=lambda c: _SEVERITY_RANK.get(c.severity.value, 0)).severity.value if concerns else None
        )
        entry["has_summary"] = (
            db.query(PatientSummary).filter(PatientSummary.patient_id == patient_id).first() is not None
        )

    return list(seen.values())


def get_patient_dossier(db: Session, patient_id) -> dict:
    """Assembles the full dossier. Caller must check doctor_has_access first."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    user = db.query(User).filter(User.id == patient.user_id).first()
    summary = db.query(PatientSummary).filter(PatientSummary.patient_id == patient_id).first()

    appointments = (
        db.query(Appointment)
        .filter(Appointment.patient_id == patient_id)
        .order_by(Appointment.appointment_date.desc())
        .all()
    )

    return {
        "patient_id": patient.id,
        "full_name": user.full_name,
        "date_of_birth": patient.date_of_birth,
        "gender": patient.gender,
        "phone_number": patient.phone_number,
        "summary": summary.summary_text if summary else None,
        "open_concerns": get_open_concerns(db, patient_id),
        "recent_visits": get_recent_visits(db, patient_id),
        "medications": get_medications(db, patient_id),
        "instructions": get_instructions(db, patient_id),
        "appointments": appointments,
    }