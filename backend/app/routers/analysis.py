from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Analysis, Document
from ..schemas import AnalysisOut
from ..services.analysis_service import analyse_document

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

@router.post("/{document_id}", response_model=AnalysisOut)
async def create_analysis(document_id: int, db: Session = Depends(get_db)):
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")

    result = await analyse_document(document.full_text, document.title or document.filename)

    analysis = document.analysis or Analysis(document_id=document.id)
    
    db.add(analysis)

    analysis.objective = result["objective"]
    analysis.methodology = result["methodology"]
    analysis.dataset = result["dataset"]
    analysis.findings = result["findings"]
    analysis.strengths = result.get("strengths", "")
    analysis.limitations = result["limitations"]
    analysis.keywords = result["keywords"]
    

    db.commit()
    db.refresh(analysis)
    return analysis
