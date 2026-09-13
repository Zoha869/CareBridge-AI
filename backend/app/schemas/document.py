# app/schemas/document.py
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: UUID
    document_type: str
    original_filename: str
    doctor_id: Optional[UUID] = None  # set when a doctor uploaded this - frontend uses it to label "shared by your doctor"
    created_at: datetime

    class Config:
        from_attributes = True