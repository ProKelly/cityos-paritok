from pydantic import BaseModel, Field


class DocumentRequest(BaseModel):
    description: str = Field(
        default="",
        description="A short note on what the user wants this document to portray "
        "(e.g. 'emphasize backend engineering for fintech roles').",
    )
    opportunity_id: str | None = None


class DocumentBlock(BaseModel):
    heading: str
    subheading: str = ""
    bullets: list[str] = Field(default_factory=list)


class CVResponse(BaseModel):
    full_name: str
    headline: str
    location: str = ""
    summary: str
    skills: list[str] = Field(default_factory=list)
    experience: list[DocumentBlock] = Field(default_factory=list)
    education: list[DocumentBlock] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)


class CoverLetterResponse(BaseModel):
    full_name: str
    salutation: str
    body_paragraphs: list[str]
    closing: str


class DocumentHistoryItem(BaseModel):
    id: str
    doc_type: str
    description: str = ""
    opportunity_id: str | None = None
    content: dict
    created_at: str | None = None