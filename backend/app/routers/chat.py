from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Document
from .auth import get_current_user
from ..services.chat_service import chat_multi_document, chat_with_document

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    question: str
    document_id: int | None = None
    document_ids: list[int] | None = None
    history: list[dict[str, str]] | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict]


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if not request.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty.",
        )

    if request.document_id:
        document = db.get(Document, request.document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found.",
            )
        result = await chat_with_document(
            document, request.question, request.history
        )
    elif request.document_ids:
        documents = (
            db.query(Document)
            .filter(Document.id.in_(request.document_ids))
            .all()
        )
        if not documents:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No documents found.",
            )
        result = await chat_multi_document(
            documents, request.question, request.history
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide document_id or document_ids.",
        )

    return ChatResponse(**result)
