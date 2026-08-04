from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routers import applications, auth, career_coach, chat, dashboard, documents, opportunities, paritok, profile, recommend, roadmap

settings = get_settings()

app = FastAPI(
    title="OpportunityOS AI",
    description="Your AI-powered opportunity navigator.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(opportunities.router)
app.include_router(recommend.router)
app.include_router(roadmap.router)
app.include_router(career_coach.router)
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(dashboard.router)
app.include_router(applications.router)
app.include_router(paritok.router)


@app.get("/")
def root():
    return {"name": "OpportunityOS AI", "status": "ok"}


@app.get("/health")
def health():
    return {"status": "healthy"}