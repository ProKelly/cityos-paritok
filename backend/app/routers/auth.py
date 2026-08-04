from fastapi import APIRouter, Depends

from app.core.deps import CurrentUser, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me")
def get_me(current_user: CurrentUser = Depends(get_current_user)):
    """Confirms the bearer token is valid and returns the identity encoded in it.
    Signup/login themselves happen client-side via Supabase Auth (email/password
    or Google OAuth) — the Nuxt app sends the resulting access_token as a Bearer
    token on every request to this API."""
    return {"id": current_user.id, "email": current_user.email}
