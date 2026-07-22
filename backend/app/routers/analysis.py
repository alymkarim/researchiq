from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Analysis, Document
from ..schemas import AnalysisOut
from ..services.analysis_service import analyse_document


router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post("/{document_id}", response_model=AnalysisOut)
async def analyse_saved_document(
    document_id: int,
    db: Session = Depends(get_db),
) -> Analysis:
    document = db.query(Document).filter(Document.id == document_id).first()

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")

    document_text = getattr(document, "extracted_text", None)
    if document_text is None:
        document_text = getattr(document, "text", None)

    if not document_text:
        raise HTTPException(
            status_code=422,
            detail="The document does not contain extractable text.",
        )

    result = await analyse_document(
        text=document_text,
        title=document.title or document.filename,
    )

    analysis = (
        db.query(Analysis)
        .filter(Analysis.document_id == document_id)
        .first()
    )

    if analysis is None:
        analysis = Analysis(document_id=document_id)
        db.add(analysis)

    analysis.summary = result.get("summary")
    analysis.objective = result.get("objective")
    analysis.methodology = result.get("methodology")
    analysis.dataset = result.get("dataset")
    analysis.findings = result.get("findings")
    analysis.strengths = result.get("strengths")
    analysis.limitations = result.get("limitations")
    analysis.keywords = result.get("keywords")
    analysis.analysis_mode = result.get("analysis_mode")

    db.commit()
    db.refresh(analysis)

    return analysis
