"""
Security utilities: verifying Supabase-issued JWT access tokens.

When a user signs in on the frontend (via Google OAuth or email/password),
Supabase Auth issues a JWT access token. The frontend sends this token
in the Authorization header on every API request.

Verification is delegated to Supabase's own Admin API (the same call
services/auth_service.py already uses for Google login) rather than
decoding the JWT locally. This avoids depending on which signing
method the project uses (legacy shared secret vs newer asymmetric
keys) - Supabase itself always knows how to validate its own tokens.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.supabase_client import get_admin_client

bearer_scheme = HTTPBearer()


class CurrentUser:
    """
    Lightweight container representing the authenticated user,
    extracted from a verified Supabase session.
    """

    def __init__(self, supabase_id: str, email: str | None, role: str):
        self.supabase_id = supabase_id
        self.email = email
        self.role = role  # "patient", "doctor", or "admin"


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> CurrentUser:
    """
    FastAPI dependency that verifies the incoming bearer token against
    Supabase and returns the authenticated user's identity and role.

    Role is read from the user's "user_metadata.role", set at signup
    time (see services/auth_service.py).
    """
    admin = get_admin_client()

    try:
        result = admin.auth.get_user(credentials.credentials)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
        )

    if result is None or result.user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
        )

    user = result.user
    role = (user.user_metadata or {}).get("role", "patient")

    return CurrentUser(supabase_id=user.id, email=user.email, role=role)