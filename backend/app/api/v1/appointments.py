"""
Appointment endpoints: /api/v1/appointments/*

Patients can create and view their own appointments. Doctors can view
appointments assigned to them (e.g. "today's appointments" for the
Doctor Dashboard, built in Phase 5).
"""

from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.deps import require_patient, require_doctor
from app.core.security import CurrentUser
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.user import User
from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate, AppointmentOut

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.post("", response_model=AppointmentOut)
def book_appointment(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_patient),
):
    """Books a new appointment for the logged-in patient."""
    patient = db.query(Patient).filter(Patient.user_id == user.supabase_id).first()
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found.")

    doctor = db.query(Doctor).filter(Doctor.id == payload.doctor_id).first()
    if doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Selected doctor does not exist.")

    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=payload.doctor_id,
        appointment_date=payload.appointment_date,
        appointment_time=payload.appointment_time,
        reason=payload.reason,
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


@router.get("/me", response_model=List[AppointmentOut])
def get_my_appointments_as_patient(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_patient),
):
    """Returns every appointment belonging to the logged-in patient, with the doctor's name attached."""
    patient = db.query(Patient).filter(Patient.user_id == user.supabase_id).first()
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found.")

    rows = (
        db.query(Appointment, User.full_name)
        .join(Doctor, Appointment.doctor_id == Doctor.id)
        .join(User, Doctor.user_id == User.id)
        .filter(Appointment.patient_id == patient.id)
        .all()
    )
    return _attach_name(rows, "doctor_name")


@router.get("/today", response_model=List[AppointmentOut])
def get_todays_appointments_as_doctor(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_doctor),
):
    """
    Returns today's appointments for the logged-in doctor, with the
    patient's name attached - the core data source for the Doctor
    Dashboard built in Phase 5.
    """
    doctor = db.query(Doctor).filter(Doctor.user_id == user.supabase_id).first()
    if doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found.")

    rows = (
        db.query(Appointment, User.full_name)
        .join(Patient, Appointment.patient_id == Patient.id)
        .join(User, Patient.user_id == User.id)
        .filter(Appointment.doctor_id == doctor.id, Appointment.appointment_date == date.today())
        .order_by(Appointment.appointment_time.asc())
        .all()
    )
    return _attach_name(rows, "patient_name")


def _attach_name(rows, field: str) -> list[Appointment]:
    """Sets an extra display-name attribute on each Appointment ORM row before serializing."""
    appointments = []
    for appointment, name in rows:
        setattr(appointment, field, name)
        appointments.append(appointment)
    return appointments