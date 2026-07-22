from collections import Counter
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from ..database import get_db
from ..models import Document
from ..schemas import CompareRequest, ComparisonOut, ComparisonPaper

router = APIRouter(prefix="/api/comparison", tags=["comparison"])

@router.post("", response_model=ComparisonOut)
def compare(request: CompareRequest, db: Session = Depends(get_db)):
    statement = (
        select(Document)
        .where(Document.id.in_(request.document_ids))
        .options(selectinload(Document.analysis))
    )
    documents = list(db.scalars(statement).all())

    if len(documents) != len(set(request.document_ids)):
        raise HTTPException(status_code=404, detail="One or more documents were not found.")

    if any(not document.analysis for document in documents):
        raise HTTPException(status_code=400, detail="Analyse every selected paper first.")

    papers = [
        ComparisonPaper(
            document_id=document.id,
            title=document.title or document.filename,
            objective=document.analysis.objective,
            methodology=document.analysis.methodology,
            dataset=document.analysis.dataset,
            findings=document.analysis.findings,
            limitations=document.analysis.limitations,
        )
        for document in documents
    ]

    counts = Counter()
    for document in documents:
        counts.update(
            keyword.strip().lower()
            for keyword in document.analysis.keywords.split(",")
            if keyword.strip()
        )

    common = [keyword for keyword, count in counts.most_common(8) if count >= 2]
    summary = f"Compared {len(papers)} papers. Common themes: {', '.join(common) if common else 'none detected yet'}."

    return ComparisonOut(papers=papers, common_keywords=common, summary=summary)
