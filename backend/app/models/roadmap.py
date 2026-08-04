from pydantic import BaseModel


class RoadmapRequest(BaseModel):
    goal: str


class RoadmapMonth(BaseModel):
    month: int
    title: str
    focus_areas: list[str]
    milestones: list[str]


class RoadmapResponse(BaseModel):
    id: str | None = None
    goal: str
    summary: str
    months: list[RoadmapMonth]


class CareerCoachRequest(BaseModel):
    opportunity_id: str | None = None


class CareerCoachResponse(BaseModel):
    cv_suggestions: list[str]
    cover_letter_draft: str
    portfolio_improvements: list[str]
    skills_to_learn: list[str]
    interview_tips: list[str]
    timeline: list[str]
