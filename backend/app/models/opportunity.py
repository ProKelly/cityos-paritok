from datetime import date

from pydantic import BaseModel, Field

CATEGORIES = [
    "Scholarships",
    "Jobs",
    "Internships",
    "Grants",
    "Competitions",
    "Accelerators",
    "Fellowships",
    "Conferences",
    "Events",
    "Volunteering",
]


class OpportunityIn(BaseModel):
    title: str
    organization: str
    description: str
    country: str = "Global"
    category: str
    deadline: date | None = None
    eligibility: str = ""
    skills: list[str] = Field(default_factory=list)
    url: str


class OpportunityOut(OpportunityIn):
    id: str
    created_at: str | None = None


class MatchResult(BaseModel):
    opportunity_id: str
    match_score: int
    reason: str
    missing_skill: str | None = None
    next_step: str
    opportunity: OpportunityOut | None = None


class RecommendResponse(BaseModel):
    matches: list[MatchResult]
