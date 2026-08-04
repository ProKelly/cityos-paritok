from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client

from app.core.deps import CurrentUser, get_current_user, get_scoped_db
from app.core.supabase_client import get_service_client
from app.models.opportunity import CATEGORIES, OpportunityIn, OpportunityOut
from app.services import embedding_service

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


@router.get("", response_model=list[OpportunityOut])
def list_opportunities(
    category: str | None = Query(default=None),
    country: str | None = Query(default=None),
    q: str | None = Query(default=None, description="keyword search in title/description"),
    limit: int = Query(default=50, le=200),
    db: Client = Depends(get_scoped_db),
):
    query = db.table("opportunities").select(
        "id,title,organization,description,country,category,deadline,eligibility,skills,url,created_at"
    )
    if category:
        query = query.eq("category", category)
    if country:
        query = query.eq("country", country)
    if q:
        query = query.or_(f"title.ilike.%{q}%,description.ilike.%{q}%")
    res = query.order("deadline", desc=False).limit(limit).execute()
    return res.data or []


@router.get("/categories")
def list_categories():
    return CATEGORIES


@router.get("/{opportunity_id}", response_model=OpportunityOut)
def get_opportunity(opportunity_id: str, db: Client = Depends(get_scoped_db)):
    res = db.table("opportunities").select("*").eq("id", opportunity_id).limit(1).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return res.data[0]


@router.post("", response_model=OpportunityOut)
def create_opportunity(
    payload: OpportunityIn,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Adds one opportunity to the knowledge base and embeds it immediately so it's
    searchable right away. Uses the service-role client since `opportunities` is a
    shared table, not user-scoped."""
    embedding_input = f"{payload.title}. {payload.description}. Skills: {', '.join(payload.skills)}"
    vector = embedding_service.embed_text(embedding_input)

    db = get_service_client()
    record = payload.model_dump(mode="json")
    record["embedding"] = vector
    record["created_by"] = current_user.id

    res = db.table("opportunities").insert(record).execute()
    if not res.data:
        raise HTTPException(status_code=500, detail="Failed to create opportunity")
    return res.data[0]


@router.post("/{opportunity_id}/save")
def save_opportunity(
    opportunity_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Client = Depends(get_scoped_db),
):
    res = db.table("saved_opportunities").upsert(
        {"user_id": current_user.id, "opportunity_id": opportunity_id}
    ).execute()
    return {"saved": True, "data": res.data}


@router.delete("/{opportunity_id}/save")
def unsave_opportunity(
    opportunity_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Client = Depends(get_scoped_db),
):
    db.table("saved_opportunities").delete().eq("user_id", current_user.id).eq(
        "opportunity_id", opportunity_id
    ).execute()
    return {"saved": False}


@router.get("/saved/list", response_model=list[OpportunityOut])
def list_saved(
    current_user: CurrentUser = Depends(get_current_user),
    db: Client = Depends(get_scoped_db),
):
    res = (
        db.table("saved_opportunities")
        .select("opportunity_id, opportunities(*)")
        .eq("user_id", current_user.id)
        .execute()
    )
    return [row["opportunities"] for row in (res.data or []) if row.get("opportunities")]
