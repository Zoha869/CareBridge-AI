"""
Patient endpoints: /api/v1/patients/*

All routes here are restricted to the authenticated patient's own
data. Patients can never read or modify another patient's records —
this is enforced by always filtering on the current user's own
patient row, never on a patient_id supplied by the client.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.deps import require_patient
from app.core.security import CurrentUser
from app.models.patient import Patient
from app.models.user import User
from app.schemas.patient import PatientOut, PatientProfileUpdate
from app.schemas.doctor_view import MedicationBrief, InstructionBrief, ConcernBrief
from app.services.patient_context_service import get_medications, get_instructions, get_open_concerns

router = APIRouter(prefix="/patients", tags=["Patients"])


def _get_own_patient_row(db: Session, user: CurrentUser) -> Patient:
    """Fetches the Patient row belonging to the currently logged-in user."""
    patient = db.query(Patient).filter(Patient.user_id == user.supabase_id).first()
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found for this account.",
        )
    user_row = db.query(User).filter(User.id == user.supabase_id).first()
    patient.full_name = user_row.full_name if user_row else None
    return patient


@router.get("/me", response_model=PatientOut)
def get_my_profile(db: Session = Depends(get_db), user: CurrentUser = Depends(require_patient)):
    """Returns the logged-in patient's own profile."""
    return _get_own_patient_row(db, user)


@router.put("/me", response_model=PatientOut)
def update_my_profile(
    payload: PatientProfileUpdate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_patient),
):
    """Updates the logged-in patient's own profile fields."""
    patient = _get_own_patient_row(db, user)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(patient, field, value)

    db.commit()
    db.refresh(patient)
    return _get_own_patient_row(db, user)


@router.get("/me/medications", response_model=List[MedicationBrief])
def get_my_medications(db: Session = Depends(get_db), user: CurrentUser = Depends(require_patient)):
    """Dashboard: the logged-in patient's own recorded medications."""
    patient = db.query(Patient).filter(Patient.user_id == user.supabase_id).first()
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found.")
    return get_medications(db, patient.id)


@router.get("/me/instructions", response_model=List[InstructionBrief])
def get_my_instructions(db: Session = Depends(get_db), user: CurrentUser = Depends(require_patient)):
    """Dashboard: the logged-in patient's own recorded doctor instructions."""
    patient = db.query(Patient).filter(Patient.user_id == user.supabase_id).first()
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found.")
    return get_instructions(db, patient.id)


@router.get("/me/concerns", response_model=List[ConcernBrief])
def get_my_concerns(db: Session = Depends(get_db), user: CurrentUser = Depends(require_patient)):
    """Dashboard: the logged-in patient's own open concerns."""
    patient = db.query(Patient).filter(Patient.user_id == user.supabase_id).first()
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found.")
    return get_open_concerns(db, patient.id)