from pathlib import Path
import shutil
import uuid
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from ..config import settings
from ..database import get_db
from ..models import Document
from ..schemas import DocumentOut
from ..services.pdf_service import extract_pdf

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.post("/upload", response_model=list[DocumentOut], status_code=201)
async def upload_documents(files: list[UploadFile] = File(...), db: Session = Depends(get_db)):
    created = []

    for file in files:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail=f"{file.filename} is not a PDF.")

        safe_name = f"{uuid.uuid4()}-{Path(file.filename or 'paper.pdf').name}"
        destination = Path(settings.upload_dir) / safe_name

        with destination.open("wb") as output:
            shutil.copyfileobj(file.file, output)

        extracted = extract_pdf(str(destination))

        document = Document(
            filename=file.filename or safe_name,
            title=extracted["title"],
            authors=extracted["authors"],
            abstract=extracted["abstract"],
            full_text=extracted["full_text"],
            file_path=str(destination),
        )
        db.add(document)
        created.append(document)

    db.commit()
    for document in created:
        db.refresh(document)

    return created

@router.get("", response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db)):
    statement = select(Document).options(selectinload(Document.analysis)).order_by(Document.created_at.desc())
    return list(db.scalars(statement).all())

@router.delete("/{document_id}", status_code=204)
def delete_document(document_id: int, db: Session = Depends(get_db)):
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")
    Path(document.file_path).unlink(missing_ok=True)
    db.delete(document)
    db.commit()
