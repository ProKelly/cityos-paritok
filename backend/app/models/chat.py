from pydantic import BaseModel


class ChatMessageIn(BaseModel):
    session_id: str | None = None
    message: str
    opportunity_id: str | None = None  # only used when starting a new session


class ChatMessageOut(BaseModel):
    role: str
    content: str
    created_at: str | None = None


class ChatReply(BaseModel):
    session_id: str
    reply: str
    messages: list[ChatMessageOut]


class ChatSessionSummary(BaseModel):
    id: str
    title: str
    opportunity_id: str | None = None
    updated_at: str | None = None
