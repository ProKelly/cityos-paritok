from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from app.core.deps import CurrentUser, get_current_user, get_scoped_db
from app.models.roadmap import RoadmapRequest, RoadmapResponse
from app.services import groq_service

router = APIRouter(prefix="/roadmap", tags=["roadmap"])


@router.post("", response_model=RoadmapResponse)
def create_roadmap(
    payload: RoadmapRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Client = Depends(get_scoped_db),
):
    profile_res = db.table("profiles").select("*").eq("user_id", current_user.id).limit(1).execute()
    profile = profile_res.data[0] if profile_res.data else None

    try:
        result = groq_service.generate_roadmap(payload.goal, profile)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI roadmap generation failed: {exc}")

    record = {"user_id": current_user.id, "goal": payload.goal, "plan": result}
    saved = db.table("roadmaps").insert(record).execute()
    roadmap_id = saved.data[0]["id"] if saved.data else None

    return RoadmapResponse(id=roadmap_id, goal=result["goal"], summary=result["summary"], months=result["months"])


@router.get("", response_model=list[RoadmapResponse])
def list_roadmaps(
    current_user: CurrentUser = Depends(get_current_user),
    db: Client = Depends(get_scoped_db),
):
    res = db.table("roadmaps").select("*").eq("user_id", current_user.id).order("created_at", desc=True).execute()
    out = []
    for row in res.data or []:
        plan = row["plan"]
        out.append(RoadmapResponse(id=row["id"], goal=plan["goal"], summary=plan["summary"], months=plan["months"]))
    return out



@router.get("/{roadmap_id}", response_model=RoadmapResponse)
def get_roadmap(
    roadmap_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Client = Depends(get_scoped_db),
):
    res = db.table("roadmaps").select("*").eq("id", roadmap_id).eq("user_id", current_user.id).limit(1).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    
    row = res.data[0]
    plan = row["plan"]
    return RoadmapResponse(id=row["id"], goal=plan["goal"], summary=plan["summary"], months=plan["months"])
