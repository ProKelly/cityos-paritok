from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from app.core.deps import CurrentUser, get_current_user, get_scoped_db
from app.models.opportunity import MatchResult, RecommendResponse
from app.services import embedding_service, groq_service

router = APIRouter(prefix="/recommend", tags=["recommend"])


@router.post("", response_model=RecommendResponse)
def recommend(
    current_user: CurrentUser = Depends(get_current_user),
    db: Client = Depends(get_scoped_db),
):
    """The core AI Matching Engine pipeline — now agentic:
    1. Load the user's profile (+ Opportunity DNA).
    2. Hand the model a search_opportunities TOOL rather than a pre-fetched list —
       the model decides the query itself and calls the tool.
    3. We execute the real semantic search (pgvector) it asked for and return the
       results as a genuine tool_result message.
    4. The model reasons over that tool result (now actually in context, not baked
       into the original prompt) and returns the final ranked, explained matches.

    Restructuring this as tool-calling (rather than stuffing candidates into one
    static prompt) matters for how this gets compressed upstream: it's the same
    tool_result / accumulating-context shape Paritok's compressor is trained on,
    instead of a single opaque user-message blob.
    """
    profile_res = db.table("profiles").select("*").eq("user_id", current_user.id).limit(1).execute()
    if not profile_res.data:
        raise HTTPException(status_code=400, detail="Create a profile first")
    profile = profile_res.data[0]

    def search_fn(query: str, limit: int) -> list[dict]:
        vector = embedding_service.embed_text(query)
        try:
            res = db.rpc(
                "match_opportunities",
                {"query_embedding": vector, "match_count": limit},
            ).execute()
            return res.data or []
        except Exception:
            # RPC not installed yet, or a transient error — fall back to a plain
            # select so the flow still returns something rather than hard-failing.
            return db.table("opportunities").select("*").limit(limit).execute().data or []

    try:
        result = groq_service.run_recommend_agent(profile, search_fn)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI matching failed: {exc}")

    ranked = result["ranked"]
    candidates_by_id = result["candidates_by_id"]

    matches = []
    for m in ranked.get("matches", []):
        opp = candidates_by_id.get(m.get("opportunity_id"))
        if not opp:
            continue
        matches.append(
            MatchResult(
                opportunity_id=m["opportunity_id"],
                match_score=m["match_score"],
                reason=m["reason"],
                missing_skill=m.get("missing_skill"),
                next_step=m["next_step"],
                opportunity=opp,
            )
        )

    # Cache the recommendation batch for the dashboard's "Recommendations" card.
    try:
        db.table("recommendations").insert(
            {"user_id": current_user.id, "results": [m.model_dump() for m in matches]}
        ).execute()
    except Exception:
        pass  # non-critical; recommendations are still returned to the caller

    return RecommendResponse(matches=matches)
