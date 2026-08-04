from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from app.core.deps import CurrentUser, get_current_user, get_scoped_db
from app.models.chat import ChatMessageIn, ChatMessageOut, ChatReply, ChatSessionSummary
from app.services import groq_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatReply)
def send_message(
    payload: ChatMessageIn,
    current_user: CurrentUser = Depends(get_current_user),
    db: Client = Depends(get_scoped_db),
):
    profile_res = db.table("profiles").select("*").eq("user_id", current_user.id).limit(1).execute()
    if not profile_res.data:
        raise HTTPException(status_code=400, detail="Create a profile first")
    profile = profile_res.data[0]

    # Start a new session, or continue an existing one — either way we load
    # every prior message and resend the full history on this turn, so it
    # genuinely accumulates rather than being a stateless one-off call.
    if payload.session_id:
        session_res = (
            db.table("chat_sessions")
            .select("*")
            .eq("id", payload.session_id)
            .eq("user_id", current_user.id)
            .limit(1)
            .execute()
        )
        if not session_res.data:
            raise HTTPException(status_code=404, detail="Chat session not found")
        session = session_res.data[0]
    else:
        title = payload.message[:60] + ("..." if len(payload.message) > 60 else "")
        created = (
            db.table("chat_sessions")
            .insert(
                {
                    "user_id": current_user.id,
                    "title": title,
                    "opportunity_id": payload.opportunity_id,
                }
            )
            .execute()
        )
        session = created.data[0]

    opportunity = None
    if session.get("opportunity_id"):
        opp_res = db.table("opportunities").select("*").eq("id", session["opportunity_id"]).limit(1).execute()
        opportunity = opp_res.data[0] if opp_res.data else None

    history_res = (
        db.table("chat_messages")
        .select("role, content, created_at")
        .eq("session_id", session["id"])
        .order("created_at")
        .execute()
    )
    history = [{"role": m["role"], "content": m["content"]} for m in (history_res.data or [])]

    try:
        reply_text = groq_service.career_chat_reply(profile, history, payload.message, opportunity)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI chat failed: {exc}")

    # Persist both turns.
    db.table("chat_messages").insert(
        [
            {"session_id": session["id"], "user_id": current_user.id, "role": "user", "content": payload.message},
            {"session_id": session["id"], "user_id": current_user.id, "role": "assistant", "content": reply_text},
        ]
    ).execute()
    db.table("chat_sessions").update({}).eq("id", session["id"]).execute()  # bumps updated_at via trigger

    all_messages = history + [
        {"role": "user", "content": payload.message},
        {"role": "assistant", "content": reply_text},
    ]

    return ChatReply(
        session_id=session["id"],
        reply=reply_text,
        messages=[ChatMessageOut(role=m["role"], content=m["content"]) for m in all_messages],
    )


@router.get("/sessions", response_model=list[ChatSessionSummary])
def list_sessions(
    current_user: CurrentUser = Depends(get_current_user),
    db: Client = Depends(get_scoped_db),
):
    res = (
        db.table("chat_sessions")
        .select("id, title, opportunity_id, updated_at")
        .eq("user_id", current_user.id)
        .order("updated_at", desc=True)
        .limit(30)
        .execute()
    )
    return res.data or []


@router.get("/sessions/{session_id}", response_model=list[ChatMessageOut])
def get_session_messages(
    session_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Client = Depends(get_scoped_db),
):
    session_res = (
        db.table("chat_sessions").select("id").eq("id", session_id).eq("user_id", current_user.id).limit(1).execute()
    )
    if not session_res.data:
        raise HTTPException(status_code=404, detail="Chat session not found")

    res = (
        db.table("chat_messages")
        .select("role, content, created_at")
        .eq("session_id", session_id)
        .order("created_at")
        .execute()
    )
    return res.data or []
