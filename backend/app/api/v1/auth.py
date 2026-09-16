"""
Authentication endpoints: /api/v1/auth/*

Exposes signup and login (both email/password and Google) so the
frontend never talks to Supabase's Auth API directly for anything
that needs to be mirrored into our own database.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.auth import (
    EmailSignupRequest,
    EmailLoginRequest,
    GoogleLoginRequest,
    AuthResponse,
    RefreshRequest,
    RefreshResponse,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=AuthResponse)
def signup(payload: EmailSignupRequest, db: Session = Depends(get_db)):
    """Registers a new patient or doctor using email + password."""
    return auth_service.signup_with_email(db, payload)


@router.post("/login", response_model=AuthResponse)
def login(payload: EmailLoginRequest, db: Session = Depends(get_db)):
    """Logs in an existing user using email + password."""
    return auth_service.login_with_email(db, payload)


@router.post("/google", response_model=AuthResponse)
def google_login(payload: GoogleLoginRequest, db: Session = Depends(get_db)):
    """
    Finalizes a Google sign-in initiated on the frontend via Supabase's
    OAuth redirect flow, and syncs the profile into our own database.
    """
    return auth_service.login_with_google(db, payload)


@router.post("/refresh", response_model=RefreshResponse)
def refresh(payload: RefreshRequest):
    """Exchanges a refresh_token for a new access_token (used after a 401)."""
    return auth_service.refresh_session(payload.refresh_token)