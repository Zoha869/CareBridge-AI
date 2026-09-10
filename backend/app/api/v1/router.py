"""
Top-level API router.

Combines every individual resource router (auth, patients, doctors,
appointments, conversations) under a single object that main.py mounts
behind the versioned "/api/v1" prefix.
"""

from fastapi import APIRouter

from app.api.v1 import auth, patients, doctors, appointments, conversations

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(patients.router)
api_router.include_router(doctors.router)
api_router.include_router(appointments.router)
api_router.include_router(conversations.router)