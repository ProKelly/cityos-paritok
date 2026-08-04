from fastapi import APIRouter, Depends
from supabase import Client

from app.core.deps import CurrentUser, get_current_user, get_scoped_db

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def dashboard_summary(
    current_user: CurrentUser = Depends(get_current_user),
    db: Client = Depends(get_scoped_db),
):
    profile_res = db.table("profiles").select("*").eq("user_id", current_user.id).limit(1).execute()
    profile = profile_res.data[0] if profile_res.data else None

    saved_res = db.table("saved_opportunities").select("opportunity_id", count="exact").eq(
        "user_id", current_user.id
    ).execute()
    applied_res = db.table("applications").select("id", count="exact").eq(
        "user_id", current_user.id
    ).execute()
    latest_rec = (
        db.table("recommendations")
        .select("results, created_at")
        .eq("user_id", current_user.id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    latest_matches = latest_rec.data[0]["results"] if latest_rec.data else []

    # Profile strength: simple completeness heuristic across key fields.
    fields = ["skills", "interests", "goals", "preferred_industries", "education_level"]
    filled = 0
    if profile:
        for f in fields:
            v = profile.get(f)
            if v:
                filled += 1
    profile_strength = round((filled / len(fields)) * 100) if profile else 0

    upcoming_deadlines = sorted(
        [m for m in latest_matches if m.get("opportunity", {}).get("deadline")],
        key=lambda m: m["opportunity"]["deadline"],
    )[:5]

    return {
        "opportunities_found": len(latest_matches),
        "saved_count": saved_res.count or 0,
        "applied_count": applied_res.count or 0,
        "upcoming_deadlines": upcoming_deadlines,
        "recommendations": latest_matches[:5],
        "profile_strength": profile_strength,
        "opportunity_dna": profile.get("opportunity_dna") if profile else None,
    }
