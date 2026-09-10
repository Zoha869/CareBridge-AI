"""
Shared FastAPI dependencies for role-based access control.

These build on top of core.security.get_current_user to restrict
specific endpoints to patients only, doctors only, or admins only.
"""

from fastapi import Depends, HTTPException, status

from app.core.security import get_current_user, CurrentUser


def require_patient(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Allows access only to users with the 'patient' role."""
    if user.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only accessible to patients.",
        )
    return user


def require_doctor(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Allows access only to users with the 'doctor' role."""
    if user.role != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only accessible to doctors.",
        )
    return user


def require_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Allows access only to users with the 'admin' role."""
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only accessible to administrators.",
        )
    return user
