"""
Authentication service layer.

Wraps Supabase Auth calls (signup, email login, Google login) and
keeps our own "users" / "patients" / "doctors" tables in sync with
Supabase's auth.users table. This is where the "two ways to log in"
requirement (Google Sign-In + Email/Password) is implemented.
"""

import uuid
from datetime import date
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.supabase_client import get_anon_client, get_admin_client
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.schemas.auth import EmailSignupRequest, EmailLoginRequest, GoogleLoginRequest


def _create_local_profile(db: Session, supabase_user_id: str, email: str, full_name: str, role: str, provider: str, specialization: str | None = None) -> User:
    """
    Creates the matching row in our own "users" table (and the
    role-specific "patients"/"doctors" row) after a successful
    Supabase signup or first-time Google login.
    """
    existing = db.query(User).filter(User.id == uuid.UUID(supabase_user_id)).first()
    if existing:
        return existing

    user = User(
        id=uuid.UUID(supabase_user_id),
        email=email,
        full_name=full_name,
        role=UserRole(role),
        auth_provider=provider,
    )
    db.add(user)
    db.flush()  # Ensures user.id is available for the profile row below.

    if role == "patient":
        db.add(Patient(user_id=user.id))
    elif role == "doctor":
        db.add(Doctor(user_id=user.id, specialization=specialization))

    db.commit()
    db.refresh(user)
    return user


def signup_with_email(db: Session, payload: EmailSignupRequest) -> dict:
    """
    Registers a new user via Supabase Auth using email + password,
    then creates the matching local profile row.
    """
    supabase = get_anon_client()

    result = supabase.auth.sign_up(
        {
            "email": payload.email,
            "password": payload.password,
            "options": {"data": {"full_name": payload.full_name, "role": payload.role}},
        }
    )

    if result.user is None or result.session is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Signup failed. The email may already be registered, or email confirmation is required.",
        )

    _create_local_profile(
        db,
        supabase_user_id=result.user.id,
        email=payload.email,
        full_name=payload.full_name,
        role=payload.role,
        provider="email",
        specialization=payload.specialization,
    )

    return {
        "access_token": result.session.access_token,
        "refresh_token": result.session.refresh_token,
        "user_id": result.user.id,
        "email": payload.email,
        "full_name": payload.full_name,
        "role": payload.role,
    }


def login_with_email(db: Session, payload: EmailLoginRequest) -> dict:
    """Authenticates an existing user via Supabase Auth email + password."""
    supabase = get_anon_client()

    try:
        result = supabase.auth.sign_in_with_password(
            {"email": payload.email, "password": payload.password}
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    user_row = db.query(User).filter(User.id == uuid.UUID(result.user.id)).first()
    if user_row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authenticated with Supabase but no local profile exists for this user.",
        )

    return {
        "access_token": result.session.access_token,
        "refresh_token": result.session.refresh_token,
        "user_id": str(user_row.id),
        "email": user_row.email,
        "full_name": user_row.full_name,
        "role": user_row.role.value,
    }


def refresh_session(refresh_token: str) -> dict:
    """
    Exchanges a refresh_token for a new access_token + refresh_token pair.
    Called by the frontend when an API request comes back 401 because
    the access_token has expired.
    """
    supabase = get_anon_client()

    try:
        result = supabase.auth.refresh_session(refresh_token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired. Please log in again.",
        )

    if result.session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired. Please log in again.",
        )

    return {
        "access_token": result.session.access_token,
        "refresh_token": result.session.refresh_token,
    }


def login_with_google(db: Session, payload: GoogleLoginRequest) -> dict:
    """
    Finalizes a Google sign-in.

    The frontend already completed the Google OAuth redirect through
    Supabase and obtained an access token. This function verifies that
    token belongs to a real Supabase session and, if this is the
    user's first Google login, creates their local profile row using
    the requested role.
    """
    admin = get_admin_client()

    try:
        supabase_user = admin.auth.get_user(payload.access_token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Google session token.",
        )

    if supabase_user is None or supabase_user.user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not verify Google account.",
        )

    google_user = supabase_user.user
    full_name = google_user.user_metadata.get("full_name") or google_user.user_metadata.get("name") or google_user.email

    user_row = _create_local_profile(
        db,
        supabase_user_id=google_user.id,
        email=google_user.email,
        full_name=full_name,
        role=payload.role,
        provider="google",
    )

    return {
        "access_token": payload.access_token,
        "user_id": str(user_row.id),
        "email": user_row.email,
        "full_name": user_row.full_name,
        "role": user_row.role.value,
    }