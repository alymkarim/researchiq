from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import Base, engine
from .routers import analysis, comparison, documents, search

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ResearchIQ API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(analysis.router)
app.include_router(search.router)
app.include_router(comparison.router)

@app.get("/health")
def health():
    return {"status": "healthy"}
