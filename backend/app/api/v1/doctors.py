# app/api/v1/doctors.py
"""
Doctor endpoints: /api/v1/doctors/*
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.deps import require_doctor
from app.core.security import CurrentUser, get_current_user
from app.models.doctor import Doctor
from app.models.user import User
from app.models.document import Document
from app.schemas.doctor import DoctorOut, DoctorProfileUpdate
from app.schemas.doctor_view import PatientBrief, PatientDossier
from app.schemas.doctor_chat import DoctorChatIn, DoctorChatOut
from app.schemas.document import DocumentOut
from app.services.doctor_view_service import list_doctor_patients, get_patient_dossier, doctor_has_access
from app.services.doctor_chat_service import answer_doctor_query
from app.services.document_service import upload_document, get_download_url

router = APIRouter(prefix="/doctors", tags=["Doctors"])

ALLOWED_DOCUMENT_TYPES = {"application/pdf"}
MAX_DOCUMENT_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


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


@router.post("/patients/{patient_id}/documents", response_model=DocumentOut)
async def upload_document_for_patient(
    patient_id: str,
    file: UploadFile = File(...),
    document_type: str = Form("other"),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_doctor),
):
    """
    Doctor uploads a document (e.g. a test result or prescription) for
    one of their patients. Only allowed if the doctor has an appointment
    with this patient. Marked visibility="SHARED" so the patient can see
    it in their own document list, and it's ingested into RAG tagged
    with this patient_id so the patient assistant can answer questions
    about it too.
    """
    doctor = db.query(Doctor).filter(Doctor.user_id == user.supabase_id).first()
    if doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found.")

    if not doctor_has_access(db, doctor.id, patient_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this patient's record.",
        )

    if file.content_type not in ALLOWED_DOCUMENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported right now.",
        )

    file_bytes = await file.read()
    if len(file_bytes) > MAX_DOCUMENT_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is too large (10 MB limit).",
        )

    document = upload_document(
        db,
        patient_id=patient_id,
        uploaded_by=user.supabase_id,
        doctor_id=doctor.id,
        document_type=document_type,
        filename=file.filename,
        file_bytes=file_bytes,
        content_type=file.content_type,
        visibility="SHARED",
    )
    return document


@router.get("/patients/{patient_id}/documents", response_model=List[DocumentOut])
def list_patient_documents_for_doctor(
    patient_id: str,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_doctor),
):
    """Every document on this patient's record (their own uploads and any
    the doctor has shared) - only accessible if the doctor has an
    appointment with this patient."""
    doctor = db.query(Doctor).filter(Doctor.user_id == user.supabase_id).first()
    if doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found.")

    if not doctor_has_access(db, doctor.id, patient_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this patient's record.",
        )

    return (
        db.query(Document)
        .filter(Document.patient_id == patient_id)
        .order_by(Document.created_at.desc())
        .all()
    )


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

    result = answer_doctor_query(db, doctor.id, payload.message, payload.patient_id, payload.patient_name_hint)
    return DoctorChatOut(**result)


@router.get("/patients/{patient_id}/documents/{document_id}/download")
def get_patient_document_download_url(
    patient_id: str,
    document_id: str,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_doctor),
):
    """Returns a short-lived signed URL to view/download one of a
    patient's documents - only if the doctor has access to this patient."""
    doctor = db.query(Doctor).filter(Doctor.user_id == user.supabase_id).first()
    if doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found.")

    if not doctor_has_access(db, doctor.id, patient_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this patient's record.",
        )

    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.patient_id == patient_id)
        .first()
    )
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    return {"url": get_download_url(document)}