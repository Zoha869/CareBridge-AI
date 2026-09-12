# backend/scripts/ingest_knowledge_base.py
"""
One-off CLI: ingest every .md/.txt file under backend/knowledge_base/
as hospital-approved general medical knowledge (category=medical_knowledge,
no patient/doctor owner - this is the content general_response_node
retrieves from).

Usage (from backend/, with venv active):
    python -m scripts.ingest_knowledge_base
"""

import pathlib
from app.services.ingestion_service import ingest_text

KB_DIR = pathlib.Path(__file__).resolve().parent.parent / "knowledge_base"


def main():
    files = sorted(KB_DIR.glob("*.md")) + sorted(KB_DIR.glob("*.txt"))
    if not files:
        print(f"No files found in {KB_DIR} - add Tab 17/18-style content there first.")
        return
    for f in files:
        count = ingest_text(f.read_text(encoding="utf-8"), category="medical_knowledge", sub_type=f.stem)
        print(f"{f.name}: {count} chunks ingested")


if __name__ == "__main__":
    main()