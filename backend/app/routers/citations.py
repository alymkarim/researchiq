from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Document
from ..services.citation_service import to_apa, to_bibtex, to_mla

router = APIRouter(prefix="/api/citations", tags=["citations"])


@router.get("/{document_id}")
def get_citation(
    document_id: int,
    format: str = "bibtex",
    db: Session = Depends(get_db),
):
    doc = db.get(Document, document_id)

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    formatters = {"bibtex": to_bibtex, "apa": to_apa, "mla": to_mla}
    formatter = formatters.get(format)

    if not formatter:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format: {format}",
        )

    return {"format": format, "citation": formatter(doc)}
