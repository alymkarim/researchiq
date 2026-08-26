from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..models import Document
from .auth import get_current_user
from ..services.summary_service import analyse_with_level

router = APIRouter(prefix="/api/summary", tags=["summary"])


class SummaryResponse(BaseModel):
    level: str
    analysis: dict | None = None
    error: str | None = None


@router.get("/{document_id}", response_model=SummaryResponse)
async def get_summary(
    document_id: int,
    level: str = Query(default="standard", pattern="^(quick|standard|deep)$"),
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

    result = await analyse_with_level(
        text=document.full_text or "",
        title=document.title or document.filename,
        level=level,
    )

    return SummaryResponse(**result)
