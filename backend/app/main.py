from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .limiter import limiter
from .routers import analysis, auth, batch, chat, citations, collaboration, comparison, documents, discovery, export, highlights, llm, recommendations, search, summary, visualizations




app = FastAPI(
    title="ResearchIQ API",
    version="1.0.0",
    description=(
        "API for uploading, analysing, searching and comparing "
        "scientific research papers."
    ),
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]

if settings.frontend_origin:
    production_origin = settings.frontend_origin.rstrip("/")

    if production_origin not in allowed_origins:
        allowed_origins.append(production_origin)


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(documents.router)
app.include_router(analysis.router)
app.include_router(search.router)
app.include_router(comparison.router)
app.include_router(auth.router)
app.include_router(citations.router)
app.include_router(recommendations.router)
app.include_router(chat.router)
app.include_router(export.router)
app.include_router(discovery.router)
app.include_router(batch.router)
app.include_router(collaboration.router)
app.include_router(llm.router)
app.include_router(summary.router)
app.include_router(highlights.router)
app.include_router(visualizations.router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": "ResearchIQ API",
        "status": "online",
        "documentation": "/docs",
    }


@app.get("/health", tags=["system"])
def simple_health() -> dict[str, str]:
    return {
        "status": "healthy",
    }


@app.get("/api/health", tags=["system"])
def health_check(
    db: Session = Depends(get_db),
) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "api": "online",
            "database": "connected",
        }

    except Exception:
        return {
            "status": "degraded",
            "api": "online",
            "database": "disconnected",
        }