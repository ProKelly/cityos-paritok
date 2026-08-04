from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
import requests

from app.core.config import get_settings
from app.core.supabase_client import get_user_client

bearer_scheme = HTTPBearer(auto_error=False)
settings = get_settings()


@dataclass
class CurrentUser:
    id: str
    email: str | None
    access_token: str


def verify_supabase_token(token: str):

    try:
        # Get Supabase public keys
        jwks_url = f"{settings.supabase_url}/auth/v1/.well-known/jwks.json"

        jwks = requests.get(jwks_url).json()

        header = jwt.get_unverified_header(token)

        key = None

        for k in jwks["keys"]:
            if k["kid"] == header["kid"]:
                key = k
                break

        if not key:
            raise Exception("Signing key not found")

        payload = jwt.decode(
            token,
            key,
            algorithms=["ES256"],
            audience="authenticated",
        )

        return payload

    except Exception as e:
        print("JWT ERROR:", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> CurrentUser:

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing auth token"
        )

    token = credentials.credentials

    payload = verify_supabase_token(token)

    user_id = payload.get("sub")
    email = payload.get("email")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject"
        )

    return CurrentUser(
        id=user_id,
        email=email,
        access_token=token,
    )


def get_scoped_db(
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Supabase client authenticated as current user.
    RLS policies will apply.
    """
    return get_user_client(current_user.access_token)