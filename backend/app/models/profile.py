from pydantic import BaseModel, Field


class ProfileIn(BaseModel):
    full_name: str
    country: str
    education_level: str
    skills: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    goals: str = ""
    preferred_industries: list[str] = Field(default_factory=list)
    preferred_countries: list[str] = Field(default_factory=list)
    availability: str = ""
    expected_salary: str | None = None
    languages: list[str] = Field(default_factory=list)
    resume_text: str | None = None


class OpportunityDNA(BaseModel):
    summary: str
    strengths: list[str]
    weaknesses: list[str]
    career_interests: list[str]
    personality_summary: str
    recommended_categories: list[str]


class ProfileOut(ProfileIn):
    id: str
    user_id: str
    opportunity_dna: OpportunityDNA | None = None
