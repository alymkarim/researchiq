from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Document
from ..schemas import SearchRequest, SearchResult
from ..services.search_service import search_documents


router = APIRouter(
    prefix="/api/search",
    tags=["search"],
)


@router.post(
    "",
    response_model=list[SearchResult],
)
def search(
    request: SearchRequest,
    db: Session = Depends(get_db),
) -> list[dict]:
    statement = select(Document)

    if request.document_ids:
        statement = statement.where(
            Document.id.in_(request.document_ids)
        )

    documents = list(
        db.scalars(statement).all()
    )

    return search_documents(
        documents=documents,
        query=request.query,
        limit=request.limit,
    )