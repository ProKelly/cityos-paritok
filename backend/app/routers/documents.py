from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from app.core.deps import CurrentUser, get_current_user, get_scoped_db
from app.models.documents import CoverLetterResponse, CVResponse, DocumentHistoryItem, DocumentRequest
from app.services import groq_service

router = APIRouter(prefix="/documents", tags=["documents"])


def _load_profile_and_opportunity(payload: DocumentRequest, current_user: CurrentUser, db: Client):
    profile_res = db.table("profiles").select("*").eq("user_id", current_user.id).limit(1).execute()
    if not profile_res.data:
        raise HTTPException(status_code=400, detail="Create a profile first")
    profile = profile_res.data[0]

    opportunity = None
    if payload.opportunity_id:
        opp_res = db.table("opportunities").select("*").eq("id", payload.opportunity_id).limit(1).execute()
        opportunity = opp_res.data[0] if opp_res.data else None

    return profile, opportunity


def _save_document(db: Client, user_id: str, doc_type: str, payload: DocumentRequest, content: dict):
    try:
        db.table("documents").insert(
            {
                "user_id": user_id,
                "doc_type": doc_type,
                "description": payload.description,
                "opportunity_id": payload.opportunity_id,
                "content": content,
            }
        ).execute()
    except Exception:
        pass  # history is a convenience, not critical — don't fail the request over it


@router.post("/cv", response_model=CVResponse)
def generate_cv(
    payload: DocumentRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Client = Depends(get_scoped_db),
):
    profile, opportunity = _load_profile_and_opportunity(payload, current_user, db)
    try:
        result = groq_service.generate_cv_document(profile, payload.description, opportunity)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI CV generation failed: {exc}")
    _save_document(db, current_user.id, "cv", payload, result)
    return CVResponse(**result)


@router.post("/cover-letter", response_model=CoverLetterResponse)
def generate_cover_letter(
    payload: DocumentRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Client = Depends(get_scoped_db),
):
    profile, opportunity = _load_profile_and_opportunity(payload, current_user, db)
    try:
        result = groq_service.generate_cover_letter_document(profile, payload.description, opportunity)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI cover letter generation failed: {exc}")
    _save_document(db, current_user.id, "cover_letter", payload, result)
    return CoverLetterResponse(**result)


@router.get("", response_model=list[DocumentHistoryItem])
def list_documents(
    doc_type: str | None = None,
    current_user: CurrentUser = Depends(get_current_user),
    db: Client = Depends(get_scoped_db),
):
    """History for the profile page — e.g. 'past CVs' / 'past cover letters'."""
    query = db.table("documents").select("*").eq("user_id", current_user.id)
    if doc_type:
        query = query.eq("doc_type", doc_type)
    res = query.order("created_at", desc=True).limit(20).execute()
    return res.data or []


@router.get("/{document_id}")
def get_document(
    document_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Client = Depends(get_scoped_db),
):
    """Fetch one saved document's content (e.g. to re-download its PDF)."""
    res = db.table("documents").select("*").eq("id", document_id).eq("user_id", current_user.id).limit(1).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Document not found")
    return res.data[0]