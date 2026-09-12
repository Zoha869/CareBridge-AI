# app/services/ingestion_service.py
"""
Splits source text into chunks and stores them in Qdrant, tagged with
the metadata schema from the CareBridge knowledge base design. Phase 7
(patient/doctor document uploads) will call this same function with
different category/patient_id/visibility values - only the tags change,
not the pipeline.
"""

import uuid
from app.services.embedding_service import embed_texts
from app.services.rag_service import ensure_collection, upsert_chunks

MAX_CHUNK_CHARS = 1200


def _split_sections(text: str) -> list[str]:
    # Knowledge base docs use "---" as a section separator (see the tab
    # structure in the CareBridge clinical knowledge base) - split there
    # first since that's already a meaningful topic boundary, then
    # hard-wrap any section still too long for one embedding chunk.
    sections = [s.strip() for s in text.split("\n---\n") if s.strip()]
    chunks = []
    for section in sections:
        if len(section) <= MAX_CHUNK_CHARS:
            chunks.append(section)
        else:
            chunks.extend(section[i : i + MAX_CHUNK_CHARS] for i in range(0, len(section), MAX_CHUNK_CHARS))
    return chunks


def ingest_text(
    text: str,
    *,
    category: str,
    sub_type: str = "general",
    patient_id=None,
    doctor_id=None,
    appointment_id=None,
    visibility: str = "SHARED",
    uploaded_by: str | None = None,
) -> int:
    ensure_collection()
    sections = _split_sections(text)
    if not sections:
        return 0

    vectors = embed_texts(sections, task="retrieval.passage")
    payload_base = {
        "category": category,
        "sub_type": sub_type,
        "patient_id": str(patient_id) if patient_id else None,
        "doctor_id": str(doctor_id) if doctor_id else None,
        "appointment_id": str(appointment_id) if appointment_id else None,
        "visibility": visibility,
        "uploaded_by": uploaded_by,
    }
    chunks = [
        {"id": str(uuid.uuid4()), "text": section, "vector": vector, "payload": payload_base}
        for section, vector in zip(sections, vectors)
    ]
    upsert_chunks(chunks)
    return len(chunks)