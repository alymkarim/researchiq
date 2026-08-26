from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Document
from ..services.recommendation_service import find_related_documents

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.get("/{document_id}")
def get_recommendations(
    document_id: int,
    limit: int = 3,
    db: Session = Depends(get_db),
):
    doc = db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    all_docs = db.query(Document).all()
    related = find_related_documents(doc, all_docs, limit=limit)

    return {"document_id": document_id, "recommendations": related}
