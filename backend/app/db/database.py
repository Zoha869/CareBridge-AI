"""
Database engine and session management.

Uses SQLAlchemy's ORM against the Supabase-hosted PostgreSQL database.
A single engine is created for the application's lifetime, and a new
session is opened/closed per request via the get_db dependency.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

# The core SQLAlchemy engine connected to the Supabase Postgres database.
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# Session factory: each request gets its own database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that all ORM models inherit from.
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that yields a database session and guarantees
    it is closed after the request finishes, even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
