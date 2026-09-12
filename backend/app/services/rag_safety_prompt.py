# app/services/rag_safety_prompt.py
"""
Clinical safety instructions shared by every RAG-grounded LLM call -
patient general-question answers now, doctor/document Q&A once Phase 7
documents are ingested. Kept as one module so both sides stay consistent
instead of drifting apart. Sourced from the CareBridge knowledge base's
"AI Retrieval Rules" / "Source Priority" / safety sections.
"""

RAG_SAFETY_RULES = """Rules for using the retrieved context below:
- Answer ONLY using the retrieved context. If it doesn't contain the
  answer, say so plainly instead of guessing or inventing information.
- Never invent diagnoses, lab results, or prescriptions.
- Never present a suspected condition as confirmed.
- Clearly separate general medical education from the patient's personal
  record - don't imply general information is specific to this patient.
- For potentially serious symptoms, recommend urgent/professional
  evaluation rather than relying only on this answer.
- Never reveal information belonging to another patient or doctor."""