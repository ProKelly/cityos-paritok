from functools import lru_cache

from supabase import Client, create_client

from app.core.config import get_settings

settings = get_settings()


@lru_cache
def get_service_client() -> Client:
    """Service-role client: bypasses RLS. Use only in trusted backend logic
    (seeding, cross-user aggregation, background jobs)."""
    return create_client(settings.supabase_url, settings.supabase_service_role_key)


def get_user_client(access_token: str) -> Client:
    """Client that carries the caller's JWT so Postgres RLS policies apply.
    Use this for anything done on behalf of a specific logged-in user."""
    client = create_client(settings.supabase_url, settings.supabase_anon_key)
    client.postgrest.auth(access_token)
    return client
