from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from .auth import get_current_user
from ..services.discovery_service import search_papers

router = APIRouter(prefix="/api/discovery", tags=["discovery"])


class PaperResult(BaseModel):
    title: str
    authors: str
    abstract: str | None = None
    year: int | None = None
    url: str = ""
    pdf_url: str = ""
    doi: str | None = None
    arxiv_id: str | None = None
    citation_count: int | None = None
    source: str = ""


class DiscoveryResponse(BaseModel):
    papers: list[PaperResult]
    total: int


@router.get("/search", response_model=DiscoveryResponse)
async def discover_papers(
    q: str = Query(..., min_length=2, description="Search query"),
    sources: str = Query(
        default="semantic_scholar,arxiv",
        description="Comma-separated sources: semantic_scholar, arxiv",
    ),
    limit: int = Query(default=10, ge=1, le=50),
    user=Depends(get_current_user),
):
    source_list = [s.strip() for s in sources.split(",") if s.strip()]
    papers = await search_papers(q, sources=source_list, limit=limit)

    return DiscoveryResponse(
        papers=[PaperResult(**p) for p in papers],
        total=len(papers),
    )
