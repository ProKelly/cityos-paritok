from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from app.core.deps import CurrentUser, get_current_user, get_scoped_db
from app.models.profile import ProfileIn, ProfileOut
from app.services import groq_service

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileOut | None)
def get_profile(
    current_user: CurrentUser = Depends(get_current_user),
    db: Client = Depends(get_scoped_db),
):
    res = db.table("profiles").select("*").eq("user_id", current_user.id).limit(1).execute()
    if not res.data:
        return None
    return res.data[0]


@router.post("", response_model=ProfileOut)
def upsert_profile(
    payload: ProfileIn,
    current_user: CurrentUser = Depends(get_current_user),
    db: Client = Depends(get_scoped_db),
):
    # 1. Generate Opportunity DNA via Groq (AI #1: profile summarization)
    try:
        dna = groq_service.generate_opportunity_dna(payload.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI profile analysis failed: {exc}")

    record = {
        "user_id": current_user.id,
        **payload.model_dump(),
        "opportunity_dna": dna,
    }

    existing = db.table("profiles").select("id").eq("user_id", current_user.id).limit(1).execute()
    if existing.data:
        res = (
            db.table("profiles")
            .update(record)
            .eq("user_id", current_user.id)
            .execute()
        )
    else:
        res = db.table("profiles").insert(record).execute()

    if not res.data:
        raise HTTPException(status_code=500, detail="Failed to save profile")
    return res.data[0]
