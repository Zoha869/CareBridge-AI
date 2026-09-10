"""
Application entry point.

Creates the FastAPI app, configures CORS for the React frontend, and
mounts the versioned API router. Run locally with:

    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_router

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for the AI-Powered Patient-Doctor Communication & Support System.",
    version="1.0.0",
)

# Allow the React frontend (running on a different origin during
# development) to call this API with credentials.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount every /auth, /patients, /doctors, /appointments route under /api/v1.
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Health"])
def health_check():
    """Simple health-check endpoint to verify the API is running."""
    return {"status": "ok", "app": settings.APP_NAME, "environment": settings.ENVIRONMENT}
