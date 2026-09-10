"""
Supabase client factory.

Supabase handles authentication for us (Google OAuth + Email/Password),
so the backend never implements its own OAuth flow. Instead, it talks
to Supabase using two different clients depending on the required
privilege level:

- anon_client: used for operations that should respect Row Level
  Security (RLS) policies as a normal authenticated user would.
- admin_client: used for privileged server-side operations (e.g.
  creating a doctor profile after signup) using the service role key.
  This key must NEVER be exposed to the frontend.
"""

from functools import lru_cache
from supabase import create_client, Client

from app.core.config import settings


@lru_cache
def get_anon_client() -> Client:
    """Returns a Supabase client scoped to the public anon key."""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)


@lru_cache
def get_admin_client() -> Client:
    """
    Returns a Supabase client using the service role key.
    Grants full access, bypassing Row Level Security — use only
    in trusted, server-side logic.
    """
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
