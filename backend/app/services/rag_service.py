# app/services/rag_service.py
"""
Qdrant Cloud (free cluster) collection setup and retrieval. One shared
collection, split by metadata rather than separate collections per
category - matches the CareBridge knowledge base's tag-based access
model (category/sub_type/visibility/patient_id/doctor_id), so Phase 7
document uploads reuse the exact same collection and search logic.
"""

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from app.core.config import settings
from app.services.embedding_service import embed_query, VECTOR_SIZE

COLLECTION = "carebridge_knowledge"

_client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)


def ensure_collection() -> None:
    if not _client.collection_exists(COLLECTION):
        _client.create_collection(
            COLLECTION,
            vectors_config=qmodels.VectorParams(size=VECTOR_SIZE, distance=qmodels.Distance.COSINE),
        )
    # Qdrant Cloud requires an explicit payload index before a field can be
    # used in a filter - create one for every field search() filters on.
    # Safe to call every time; already-indexed fields just raise and get
    # skipped, so calling this from search() as well as ingestion keeps
    # the index in place no matter which one ran first.
    for field in ("category", "patient_id", "doctor_id", "visibility"):
        try:
            _client.create_payload_index(
                COLLECTION, field_name=field, field_schema=qmodels.PayloadSchemaType.KEYWORD
            )
        except Exception:
            pass


def upsert_chunks(chunks: list[dict]) -> None:
    """chunks: [{"id": str, "text": str, "vector": list[float], "payload": dict}]"""
    _client.upsert(
        collection_name=COLLECTION,
        points=[
            qmodels.PointStruct(id=c["id"], vector=c["vector"], payload={**c["payload"], "text": c["text"]})
            for c in chunks
        ],
    )


def search(
    query: str,
    *,
    category: str | None = None,
    patient_id=None,
    doctor_id=None,
    visibility_in: list[str] | None = None,
    top_k: int = 4,
) -> list[dict]:
    """Generic permission-aware search - filters are AND'd together.
    Used directly for now only by search_medical_knowledge(); the filter
    args exist so Phase 7 (patient/doctor document RAG) can call this
    same function instead of writing new retrieval logic."""
    ensure_collection()  # guarantees the payload index exists before filtering

    conditions = []
    if category:
        conditions.append(qmodels.FieldCondition(key="category", match=qmodels.MatchValue(value=category)))
    if patient_id:
        conditions.append(qmodels.FieldCondition(key="patient_id", match=qmodels.MatchValue(value=str(patient_id))))
    if doctor_id:
        conditions.append(qmodels.FieldCondition(key="doctor_id", match=qmodels.MatchValue(value=str(doctor_id))))
    if visibility_in:
        conditions.append(qmodels.FieldCondition(key="visibility", match=qmodels.MatchAny(any=visibility_in)))

    response = _client.query_points(
        collection_name=COLLECTION,
        query=embed_query(query),
        query_filter=qmodels.Filter(must=conditions) if conditions else None,
        limit=top_k,
    )
    return [
        {"text": r.payload.get("text", ""), "sub_type": r.payload.get("sub_type"), "score": r.score}
        for r in response.points
    ]


def search_medical_knowledge(query: str, top_k: int = 2) -> list[dict]:
    """Hospital-approved general knowledge (Tab 17-18: education, medication
    info) - no patient/doctor filter, this category has no owner.
    top_k=2 chosen via the retrieval-eval sweep (see EVAL.md)."""
    return search(query, category="medical_knowledge", top_k=top_k)


def search_patient_documents(patient_id, query: str, top_k: int = 2) -> list[dict]:
    """A specific patient's own uploaded documents (Tab 13) - filtered by
    patient_id so a patient's chat can never surface another patient's
    document, even though they share the same Qdrant collection."""
    return search(query, category="patient_document", patient_id=patient_id, top_k=top_k)