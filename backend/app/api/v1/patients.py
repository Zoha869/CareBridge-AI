"""
Patient endpoints: /api/v1/patients/*

All routes here are restricted to the authenticated patient's own
data. Patients can never read or modify another patient's records —
this is enforced by always filtering on the current user's own
patient row, never on a patient_id supplied by the client.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.deps import require_patient
from app.core.security import CurrentUser
from app.models.patient import Patient
from app.models.user import User
from app.models.document import Document
from app.schemas.patient import PatientOut, PatientProfileUpdate
from app.schemas.doctor_view import MedicationBrief, InstructionBrief, ConcernBrief
from app.schemas.document import DocumentOut
from app.services.patient_context_service import get_medications, get_instructions, get_open_concerns
from app.services.document_service import upload_document, get_download_url

router = APIRouter(prefix="/patients", tags=["Patients"])

ALLOWED_DOCUMENT_TYPES = {"application/pdf"}
MAX_DOCUMENT_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


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


@router.post("/me/documents", response_model=DocumentOut)
async def upload_my_document(
    file: UploadFile = File(...),
    document_type: str = Form("other"),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_patient),
):
    """
    Uploads a document to the patient's own record (PDF only for now).
    The extracted text is also ingested into the RAG index, so the
    patient assistant can answer questions about it going forward.
    """
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

    patient = _get_own_patient_row(db, user)
    document = upload_document(
        db,
        patient_id=patient.id,
        uploaded_by=user.supabase_id,
        document_type=document_type,
        filename=file.filename,
        file_bytes=file_bytes,
        content_type=file.content_type,
    )
    return document


@router.get("/me/documents", response_model=List[DocumentOut])
def list_my_documents(db: Session = Depends(get_db), user: CurrentUser = Depends(require_patient)):
    """Lists the logged-in patient's own uploaded documents, most recent first."""
    patient = _get_own_patient_row(db, user)
    return (
        db.query(Document)
        .filter(Document.patient_id == patient.id)
        .order_by(Document.created_at.desc())
        .all()
    )


@router.get("/me/documents/{document_id}/download")
def get_my_document_download_url(
    document_id: str,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_patient),
):
    """Returns a short-lived signed URL to view/download one of the
    logged-in patient's own documents."""
    patient = _get_own_patient_row(db, user)
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.patient_id == patient.id)
        .first()
    )
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    return {"url": get_download_url(document)}