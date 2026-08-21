import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..models import Document
from .auth import get_current_user
from ..services.highlight_service import map_analysis_to_pages, get_page_references

router = APIRouter(prefix="/api/highlights", tags=["highlights"])


class PageHighlight(BaseModel):
    page: int
    fields: list[dict]


class HighlightResponse(BaseModel):
    document_id: int
    page_highlights: dict[int, list[dict]]
    references: list[dict]


@router.get("/{document_id}", response_model=HighlightResponse)
def get_highlights(
    document_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    document = (
        db.query(Document)
        .options(selectinload(Document.analysis))
        .filter(Document.id == document_id)
        .first()
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")

    if not document.analysis:
        raise HTTPException(
            status_code=400,
            detail="Document has not been analysed yet.",
        )

    analysis = {
        "summary": document.analysis.summary or "",
        "objective": document.analysis.objective or "",
        "methodology": document.analysis.methodology or "",
        "dataset": document.analysis.dataset or "",
        "findings": document.analysis.findings or "",
        "strengths": document.analysis.strengths or "",
        "limitations": document.analysis.limitations or "",
        "keywords": document.analysis.keywords or "",
    }

    pages = []
    if document.pages_json:
        try:
            pages = json.loads(document.pages_json)
        except (json.JSONDecodeError, TypeError):
            pass

    if not pages:
        pages = [{"page": 1, "text": document.full_text or ""}]

    page_highlights = map_analysis_to_pages(analysis, pages)
    references = get_page_references(document.full_text or "", analysis)

    return HighlightResponse(
        document_id=document_id,
        page_highlights=page_highlights,
        references=references,
    )
