from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..models import Analysis, Document
from .auth import get_current_user
from ..services.export_service import export_analysis_docx, export_analysis_pdf

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/analysis/{document_id}/pdf")
def export_analysis_as_pdf(
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
        "summary": document.analysis.summary or "",
        "objective": document.analysis.objective or "",
        "methodology": document.analysis.methodology or "",
        "dataset": document.analysis.dataset or "",
        "findings": document.analysis.findings or "",
        "strengths": document.analysis.strengths or "",
        "limitations": document.analysis.limitations or "",
        "keywords": document.analysis.keywords or "",
        "analysis_mode": document.analysis.analysis_mode or "unknown",
    }

    pdf_bytes = export_analysis_pdf(
        title=document.title or document.filename,
        authors=document.authors,
        analysis=analysis,
    )

    filename = f"{(document.title or 'analysis').replace(' ', '_')}.pdf"
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/analysis/{document_id}/docx")
def export_analysis_as_docx(
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
        "summary": document.analysis.summary or "",
        "objective": document.analysis.objective or "",
        "methodology": document.analysis.methodology or "",
        "dataset": document.analysis.dataset or "",
        "findings": document.analysis.findings or "",
        "strengths": document.analysis.strengths or "",
        "limitations": document.analysis.limitations or "",
        "keywords": document.analysis.keywords or "",
        "analysis_mode": document.analysis.analysis_mode or "unknown",
    }

    docx_bytes = export_analysis_docx(
        title=document.title or document.filename,
        authors=document.authors,
        analysis=analysis,
    )

    filename = f"{(document.title or 'analysis').replace(' ', '_')}.docx"
    return StreamingResponse(
        iter([docx_bytes]),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
