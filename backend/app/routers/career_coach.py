from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from app.core.deps import CurrentUser, get_current_user, get_scoped_db
from app.models.roadmap import CareerCoachRequest, CareerCoachResponse
from app.services import groq_service

router = APIRouter(prefix="/career-coach", tags=["career-coach"])


@router.post("", response_model=CareerCoachResponse)
def prepare_me(
    payload: CareerCoachRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Client = Depends(get_scoped_db),
):
    profile_res = db.table("profiles").select("*").eq("user_id", current_user.id).limit(1).execute()
    if not profile_res.data:
        raise HTTPException(status_code=400, detail="Create a profile first")
    profile = profile_res.data[0]

    opportunity = None
    if payload.opportunity_id:
        opp_res = db.table("opportunities").select("*").eq("id", payload.opportunity_id).limit(1).execute()
        opportunity = opp_res.data[0] if opp_res.data else None

    try:
        result = groq_service.generate_career_coach_output(profile, opportunity)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI career coaching failed: {exc}")

    return CareerCoachResponse(**result)
