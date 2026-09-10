"""
Pydantic schemas for reading user profile data back to the client.
"""

import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserOut(BaseModel):
    """Public-facing representation of a user record."""

    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True
