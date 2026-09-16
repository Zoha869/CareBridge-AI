"""
Pydantic schemas for authentication requests and responses.

These validate incoming request bodies and shape outgoing responses
for the /auth endpoints. Actual credential verification is delegated
to Supabase — these schemas only describe the data shape.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class EmailSignupRequest(BaseModel):
    """Payload for registering a new user with email + password."""

    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str
    role: str = Field(pattern="^(patient|doctor)$")
    specialization: Optional[str] = None  # only meaningful when role="doctor"


class EmailLoginRequest(BaseModel):
    """Payload for logging in with email + password."""

    email: EmailStr
    password: str


class GoogleLoginRequest(BaseModel):
    """
    Payload for completing a Google sign-in.

    The frontend performs the actual Google OAuth redirect via
    Supabase (supabase.auth.signInWithOAuth); once Supabase returns
    an access token, the frontend sends it here so the backend can
    ensure a matching profile row exists in our own "users" table.
    """

    access_token: str
    role: str = Field(default="patient", pattern="^(patient|doctor)$")


class AuthResponse(BaseModel):
    """Standard response returned after successful signup or login."""

    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    user_id: str
    email: EmailStr
    full_name: str
    role: str


class RefreshRequest(BaseModel):
    """Payload for exchanging a refresh_token for a new access_token."""

    refresh_token: str


class RefreshResponse(BaseModel):
    """Response after successfully refreshing a session."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"