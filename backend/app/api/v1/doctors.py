# app/api/v1/doctors.py
"""
Doctor endpoints: /api/v1/doctors/*
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.deps import require_doctor
from app.core.security import CurrentUser, get_current_user
from app.models.doctor import Doctor
from app.models.user import User
from app.schemas.doctor import DoctorOut, DoctorProfileUpdate
from app.schemas.doctor_view import PatientBrief, PatientDossier
from app.schemas.doctor_chat import DoctorChatIn, DoctorChatOut
from app.services.doctor_view_service import list_doctor_patients, get_patient_dossier, doctor_has_access
from app.services.doctor_chat_service import answer_doctor_query

router = APIRouter(prefix="/doctors", tags=["Doctors"])


def _get_own_doctor_row(db: Session, user: CurrentUser) -> Doctor:
    """Fetches the Doctor row belonging to the currently logged-in user."""
    doctor = db.query(Doctor).filter(Doctor.user_id == user.supabase_id).first()
    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found for this account.",
        )
    user_row = db.query(User).filter(User.id == user.supabase_id).first()
    doctor.full_name = user_row.full_name if user_row else None
    return doctor


@router.get("/me", response_model=DoctorOut)
def get_my_profile(db: Session = Depends(get_db), user: CurrentUser = Depends(require_doctor)):
    """Returns the logged-in doctor's own profile."""
    return _get_own_doctor_row(db, user)


@router.put("/me", response_model=DoctorOut)
def update_my_profile(
    payload: DoctorProfileUpdate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_doctor),
):
    """Updates the logged-in doctor's own profile fields."""
    doctor = _get_own_doctor_row(db, user)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(doctor, field, value)

    db.commit()
    db.refresh(doctor)
    return _get_own_doctor_row(db, user)


@router.get("", response_model=List[DoctorOut])
def list_doctors(db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    """Lists all doctors - used by patients when booking an appointment."""
    rows = db.query(Doctor, User.full_name).join(User, Doctor.user_id == User.id).all()

    doctors = []
    for doctor, full_name in rows:
        doctor.full_name = full_name
        doctors.append(doctor)
    return doctors


@router.get("/patients", response_model=List[PatientBrief])
def get_my_patients(db: Session = Depends(get_db), user: CurrentUser = Depends(require_doctor)):
    """Doctor Dashboard: every patient this doctor has an appointment with."""
    doctor = db.query(Doctor).filter(Doctor.user_id == user.supabase_id).first()
    if doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found.")

    return list_doctor_patients(db, doctor.id)


@router.get("/patients/{patient_id}", response_model=PatientDossier)
def get_patient_detail(
    patient_id: str,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_doctor),
):
    """Full patient dossier - only accessible if the doctor has an appointment with this patient."""
    doctor = db.query(Doctor).filter(Doctor.user_id == user.supabase_id).first()
    if doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found.")

    if not doctor_has_access(db, doctor.id, patient_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this patient's record.",
        )

    return get_patient_dossier(db, patient_id)


@router.post("/chat", response_model=DoctorChatOut)
def doctor_chat(
    payload: DoctorChatIn,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_doctor),
):
    """Doctor AI Assistant - ask about schedule/patients, or (with a selected
    patient) prescribe a medicine, give an instruction, or mark a visit."""
    doctor = db.query(Doctor).filter(Doctor.user_id == user.supabase_id).first()
    if doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found.")

    if payload.patient_id and not doctor_has_access(db, doctor.id, payload.patient_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this patient's record.",
        )

    response = answer_doctor_query(db, doctor.id, payload.message, payload.patient_id, payload.patient_name_hint)
    return DoctorChatOut(response=response)