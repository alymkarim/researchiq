import json
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..models import Analysis, Document, SharedSession
from .auth import get_current_user

router = APIRouter(prefix="/api/share", tags=["share"])


class ShareRequest(BaseModel):
    document_ids: list[int]
    title: str = "Shared Research Session"


class ShareResponse(BaseModel):
    share_id: str
    url: str
    title: str
    expires_at: datetime | None


class SharedSessionOut(BaseModel):
    share_id: str
    title: str
    document_ids: list[int]
    documents: list[dict]
    analyses: list[dict]
    created_at: datetime


@router.post("", response_model=ShareResponse)
def create_share(
    body: ShareRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if not body.document_ids:
        raise HTTPException(status_code=400, detail="No documents selected.")

    documents = (
        db.query(Document)
        .options(selectinload(Document.analysis))
        .filter(Document.id.in_(body.document_ids))
        .all()
    )

    if not documents:
        raise HTTPException(status_code=404, detail="No documents found.")

    share_id = secrets.token_urlsafe(8)[:10]
    expires_at = datetime.utcnow() + timedelta(days=30)

    analyses = {}
    for doc in documents:
        if doc.analysis:
            analyses[doc.id] = {
                "summary": doc.analysis.summary,
                "objective": doc.analysis.objective,
                "methodology": doc.analysis.methodology,
                "findings": doc.analysis.findings,
                "strengths": doc.analysis.strengths,
                "limitations": doc.analysis.limitations,
                "keywords": doc.analysis.keywords,
            }

    session = SharedSession(
        share_id=share_id,
        title=body.title,
        document_ids=json.dumps(body.document_ids),
        analysis_data=json.dumps(analyses),
        expires_at=expires_at,
    )
    db.add(session)
    db.commit()

    return ShareResponse(
        share_id=share_id,
        url=f"/shared/{share_id}",
        title=body.title,
        expires_at=expires_at,
    )


@router.get("/{share_id}", response_model=SharedSessionOut)
def get_share(
    share_id: str,
    db: Session = Depends(get_db),
):
    session = (
        db.query(SharedSession)
        .filter(SharedSession.share_id == share_id)
        .first()
    )

    if not session:
        raise HTTPException(status_code=404, detail="Shared session not found.")

    if session.expires_at and session.expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="This shared session has expired.")

    document_ids = json.loads(session.document_ids)
    documents = (
        db.query(Document)
        .filter(Document.id.in_(document_ids))
        .all()
    )

    analyses = json.loads(session.analysis_data) if session.analysis_data else {}

    return SharedSessionOut(
        share_id=session.share_id,
        title=session.title,
        document_ids=document_ids,
        documents=[
            {"id": d.id, "title": d.title or d.filename, "authors": d.authors}
            for d in documents
        ],
        analyses=[
            {"document_id": doc_id, **data}
            for doc_id, data in analyses.items()
        ],
        created_at=session.created_at,
    )
