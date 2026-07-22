from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Document
from ..schemas import SearchRequest, SearchResult
from ..services.search_service import search_documents

router = APIRouter(prefix="/api/search", tags=["search"])

@router.post("", response_model=list[SearchResult])
def search(request: SearchRequest, db: Session = Depends(get_db)):
    documents = list(db.scalars(select(Document)).all())
    return search_documents(documents, request.query, request.limit)
