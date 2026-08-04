from fastapi import APIRouter, Depends
from pydantic import BaseModel
from supabase import Client

from app.core.deps import CurrentUser, get_current_user, get_scoped_db

router = APIRouter(prefix="/applications", tags=["applications"])


class ApplicationIn(BaseModel):
    opportunity_id: str
    status: str = "applied"  # applied | interviewing | offered | rejected
    notes: str | None = None


@router.get("")
def list_applications(
    current_user: CurrentUser = Depends(get_current_user),
    db: Client = Depends(get_scoped_db),
):
    res = (
        db.table("applications")
        .select("id, status, notes, created_at, opportunity_id, opportunities(*)")
        .eq("user_id", current_user.id)
        .order("created_at", desc=True)
        .execute()
    )
    return res.data or []


@router.post("")
def mark_applied(
    payload: ApplicationIn,
    current_user: CurrentUser = Depends(get_current_user),
    db: Client = Depends(get_scoped_db),
):
    record = {"user_id": current_user.id, **payload.model_dump()}
    res = db.table("applications").upsert(record, on_conflict="user_id,opportunity_id").execute()
    return res.data[0] if res.data else record
