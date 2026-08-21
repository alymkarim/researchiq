from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..models import Document
from .auth import get_current_user
from ..services.batch_service import batch_analyse

router = APIRouter(prefix="/api/batch", tags=["batch"])


class BatchAnalyseRequest(BaseModel):
    document_ids: list[int]


class BatchAnalyseResponse(BaseModel):
    results: list[dict]
    total: int
    successful: int
    failed: int


@router.post("/analyse", response_model=BatchAnalyseResponse)
async def batch_analyse_documents(
    request: BatchAnalyseRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if not request.document_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No document IDs provided.",
        )

    if len(request.document_ids) > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 20 documents per batch.",
        )

    documents = (
        db.query(Document)
        .options(selectinload(Document.analysis))
        .filter(Document.id.in_(request.document_ids))
        .all()
    )

    if not documents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No documents found.",
        )

    results = await batch_analyse(documents)

    successful = sum(1 for r in results if r["status"] == "success")
    failed = sum(1 for r in results if r["status"] == "error")

    return BatchAnalyseResponse(
        results=results,
        total=len(results),
        successful=successful,
        failed=failed,
    )
