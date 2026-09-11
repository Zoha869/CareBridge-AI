"""
Appointment booking logic used by the patient assistant's LangGraph
workflow. Wraps the same Appointment model used by the manual booking
endpoint in api/v1/appointments.py.
"""

from datetime import date, time
from sqlalchemy.orm import Session
from app.models.appointment import Appointment, AppointmentStatus
from app.models.doctor import Doctor
from app.models.user import User


def get_available_doctors(db: Session) -> list[dict]:
    """
    Returns id/name/specialization for every doctor, so the LLM can
    match a patient's spoken doctor name to an actual doctor_id -
    patients say "Dr. Ahmed", not a UUID.
    """
    rows = db.query(Doctor.id, User.full_name, Doctor.specialization).join(User, Doctor.user_id == User.id).all()
    return [
        {"id": str(row.id), "name": row.full_name, "specialization": row.specialization}
        for row in rows
    ]


def reschedule_appointment(db: Session, appointment_id, appointment_date: date, appointment_time: time) -> Appointment | None:
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if appointment is None:
        return None
    appointment.appointment_date = appointment_date
    appointment.appointment_time = appointment_time
    db.commit()
    db.refresh(appointment)
    return appointment


def is_slot_available(
    db: Session, doctor_id, appointment_date: date, appointment_time: time, exclude_appointment_id=None
) -> bool:
    query = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date == appointment_date,
        Appointment.appointment_time == appointment_time,
        Appointment.status != AppointmentStatus.CANCELLED,
    )
    if exclude_appointment_id:
        query = query.filter(Appointment.id != exclude_appointment_id)
    return query.first() is None


def create_appointment(
    db: Session, patient_id, doctor_id, appointment_date: date, appointment_time: time, reason: str
) -> Appointment:
    appointment = Appointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
        reason=reason,
        status=AppointmentStatus.CONFIRMED,
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


def get_patient_appointments(db: Session, patient_id) -> list[dict]:
    """
    Lists the patient's own upcoming (non-cancelled) appointments with
    doctor names, for the LLM to match against when cancelling.
    """
    rows = (
        db.query(Appointment, User.full_name)
        .join(Doctor, Appointment.doctor_id == Doctor.id)
        .join(User, Doctor.user_id == User.id)
        .filter(Appointment.patient_id == patient_id, Appointment.status != AppointmentStatus.CANCELLED)
        .order_by(Appointment.appointment_date.desc())
        .all()
    )
    return [
        {
            "id": str(appt.id),
            "doctor_name": name,
            "date": str(appt.appointment_date),
            "time": str(appt.appointment_time),
            "reason": appt.reason,
        }
        for appt, name in rows
    ]


def cancel_appointment(db: Session, appointment_id) -> Appointment | None:
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if appointment is None:
        return None
    appointment.status = AppointmentStatus.CANCELLED
    db.commit()
    db.refresh(appointment)
    return appointment