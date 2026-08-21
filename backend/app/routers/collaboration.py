from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Annotation, Document, Note
from .auth import get_current_user

router = APIRouter(prefix="/api/collaboration", tags=["collaboration"])


class NoteCreate(BaseModel):
    document_id: int
    content: str
    page_number: int | None = None


class NoteOut(BaseModel):
    id: int
    document_id: int
    content: str
    page_number: int | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AnnotationCreate(BaseModel):
    document_id: int
    page_number: int
    highlight_text: str
    comment: str | None = None
    color: str = "#ffd547"


class AnnotationOut(BaseModel):
    id: int
    document_id: int
    page_number: int
    highlight_text: str
    comment: str | None
    color: str
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/notes", response_model=NoteOut, status_code=201)
def create_note(
    body: NoteCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    document = db.get(Document, body.document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")

    note = Note(
        user_id=user.id,
        document_id=body.document_id,
        content=body.content,
        page_number=body.page_number,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.get("/notes/{document_id}", response_model=list[NoteOut])
def get_notes(
    document_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    notes = (
        db.query(Note)
        .filter(Note.document_id == document_id, Note.user_id == user.id)
        .order_by(Note.created_at.desc())
        .all()
    )
    return notes


@router.delete("/notes/{note_id}")
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    note = (
        db.query(Note)
        .filter(Note.id == note_id, Note.user_id == user.id)
        .first()
    )
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")

    db.delete(note)
    db.commit()
    return {"detail": "Note deleted."}


@router.post("/annotations", response_model=AnnotationOut, status_code=201)
def create_annotation(
    body: AnnotationCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    document = db.get(Document, body.document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")

    annotation = Annotation(
        user_id=user.id,
        document_id=body.document_id,
        page_number=body.page_number,
        highlight_text=body.highlight_text,
        comment=body.comment,
        color=body.color,
    )
    db.add(annotation)
    db.commit()
    db.refresh(annotation)
    return annotation


@router.get("/annotations/{document_id}", response_model=list[AnnotationOut])
def get_annotations(
    document_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    annotations = (
        db.query(Annotation)
        .filter(Annotation.document_id == document_id, Annotation.user_id == user.id)
        .order_by(Annotation.created_at.desc())
        .all()
    )
    return annotations


@router.delete("/annotations/{annotation_id}")
def delete_annotation(
    annotation_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    annotation = (
        db.query(Annotation)
        .filter(Annotation.id == annotation_id, Annotation.user_id == user.id)
        .first()
    )
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found.")

    db.delete(annotation)
    db.commit()
    return {"detail": "Annotation deleted."}
