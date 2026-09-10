"""
User model.

Mirrors a subset of Supabase's built-in "auth.users" table so the
application database can store role and profile information without
duplicating authentication logic. The "id" here is always the same
UUID as the corresponding Supabase auth user.
"""

import uuid
import enum
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.database import Base


class UserRole(str, enum.Enum):
    """Defines the three account types supported by the system."""

    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"


class User(Base):
    """
    Application-level user record.
    Linked one-to-one with Supabase Auth via matching UUID.
    """

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.PATIENT)
    auth_provider = Column(String, nullable=False, default="email")  # "email" or "google"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
