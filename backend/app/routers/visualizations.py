import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..models import Document
from .auth import get_current_user
from ..services.visualization_service import (
    generate_citation_graph,
    generate_keyword_network,
    generate_methodology_timeline,
    generate_word_cloud_data,
)

router = APIRouter(prefix="/api/visualizations", tags=["visualizations"])


class WordCloudItem(BaseModel):
    text: str
    value: int
    size: int


class NetworkNode(BaseModel):
    id: str
    label: str
    size: int


class NetworkEdge(BaseModel):
    source: str
    target: str
    weight: int


class KeywordNetwork(BaseModel):
    nodes: list[NetworkNode]
    edges: list[NetworkEdge]


class TimelineStep(BaseModel):
    step: int
    description: str


@router.get("/wordcloud/{document_id}", response_model=list[WordCloudItem])
def get_word_cloud(
    document_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")

    text = document.full_text or ""
    data = generate_word_cloud_data(text)
    return [WordCloudItem(**item) for item in data]


@router.get("/keyword-network/{document_id}", response_model=KeywordNetwork)
def get_keyword_network(
    document_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")

    text = document.full_text or ""
    data = generate_keyword_network(text)
    return KeywordNetwork(
        nodes=[NetworkNode(**n) for n in data["nodes"]],
        edges=[NetworkEdge(**e) for e in data["edges"]],
    )


@router.get("/methodology-timeline/{document_id}", response_model=list[TimelineStep])
def get_methodology_timeline(
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
        "methodology": document.analysis.methodology or "",
    }

    data = generate_methodology_timeline(analysis)
    return [TimelineStep(**item) for item in data]


@router.get("/citation-graph")
def get_citation_graph(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    documents = db.query(Document).all()

    doc_list = [
        {
            "id": doc.id,
            "title": doc.title or doc.filename,
            "authors": doc.authors or "",
        }
        for doc in documents
    ]

    data = generate_citation_graph(doc_list)
    return data
