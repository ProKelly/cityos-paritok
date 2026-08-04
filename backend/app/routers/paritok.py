from fastapi import APIRouter, HTTPException

from app.core.config import get_settings
from app.services import paritok_client

router = APIRouter(prefix="/paritok", tags=["paritok"])
settings = get_settings()


@router.get("/stats")
def paritok_stats():
    """Our own running totals for calls made to Paritok's hosted compress
    endpoint (character-based, since we don't tokenize client-side) — useful
    for a demo screen. Cross-check exact token/cost figures on the Paritok
    dashboard, which tracks by API key server-side."""
    if not settings.paritok_enabled:
        raise HTTPException(status_code=404, detail="Paritok is not enabled on this deployment")
    return paritok_client.get_local_stats()
