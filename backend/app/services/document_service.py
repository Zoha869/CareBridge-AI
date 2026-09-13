# app/services/document_service.py
"""
Handles a document upload end-to-end - by a patient for themselves, or
by a doctor on behalf of one of their patients: extract text from the
PDF, store the file in Supabase Storage, save the metadata row, and
ingest the extracted text into Qdrant so the patient assistant can
answer questions about it. Reuses the exact same ingestion pipeline
and metadata schema as the hospital knowledge base (see
RAG_DESIGN_DECISIONS.md) - only the tag values differ.
"""

import io
import uuid
from pypdf import PdfReader
from sqlalchemy.orm import Session

from app.core.supabase_client import get_admin_client
from app.models.document import Document
from app.services.ingestion_service import ingest_text

STORAGE_BUCKET = "patient-documents"


def extract_pdf_text(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    return "\n\n".join(page.extract_text() or "" for page in reader.pages).strip()


def upload_document(
    db: Session,
    *,
    patient_id,
    uploaded_by,
    document_type: str,
    filename: str,
    file_bytes: bytes,
    content_type: str,
    doctor_id=None,
    visibility: str = "PRIVATE",
) -> Document:
    """
    visibility="PRIVATE" (default) is for a patient uploading their own
    document - only that patient sees it. visibility="SHARED" is used
    for doctor uploads (e.g. test results, prescriptions) - the patient
    can see these too, since the patient's document list is never
    filtered by uploader, only by patient_id.
    """
    extracted_text = extract_pdf_text(file_bytes) if content_type == "application/pdf" else ""

    storage_path = f"{patient_id}/{uuid.uuid4()}_{filename}"
    get_admin_client().storage.from_(STORAGE_BUCKET).upload(
        storage_path, file_bytes, {"content-type": content_type}
    )

    document = Document(
        patient_id=patient_id,
        uploaded_by=uploaded_by,
        doctor_id=doctor_id,
        document_type=document_type,
        original_filename=filename,
        storage_path=storage_path,
        extracted_text=extracted_text or None,
        visibility=visibility,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    if extracted_text:
        # patient_id here is what search_patient_documents() filters on -
        # this document is never returned for any other patient's query,
        # whether it was the patient or their doctor who uploaded it.
        ingest_text(
            extracted_text,
            category="patient_document",
            sub_type=document_type,
            patient_id=patient_id,
            doctor_id=doctor_id,
            visibility=visibility,
            uploaded_by=str(uploaded_by),
        )

    return document


def get_download_url(document: Document, expires_in: int = 300) -> str:
    """Generates a short-lived signed URL for viewing/downloading a
    document from the private Supabase Storage bucket - the frontend
    never gets a service-role key, so this is the only way it can
    reach a file."""
    result = get_admin_client().storage.from_(STORAGE_BUCKET).create_signed_url(
        document.storage_path, expires_in
    )
    return result["signedURL"] if "signedURL" in result else result["signedUrl"]