from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Collection, Document, DocumentCollection
from .auth import get_current_user

router = APIRouter(prefix="/api/collections", tags=["collections"])


class CollectionCreate(BaseModel):
    name: str
    description: str | None = None
    color: str = "#6c5ce7"


class CollectionOut(BaseModel):
    id: int
    name: str
    description: str | None
    color: str
    created_at: datetime
    document_count: int = 0

    class Config:
        from_attributes = True


class CollectionDetail(BaseModel):
    id: int
    name: str
    description: str | None
    color: str
    created_at: datetime
    documents: list[dict] = []

    class Config:
        from_attributes = True


@router.get("", response_model=list[CollectionOut])
def list_collections(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    collections = db.query(Collection).order_by(Collection.created_at.desc()).all()
    result = []
    for c in collections:
        count = db.query(DocumentCollection).filter(DocumentCollection.collection_id == c.id).count()
        result.append(CollectionOut(
            id=c.id,
            name=c.name,
            description=c.description,
            color=c.color,
            created_at=c.created_at,
            document_count=count,
        ))
    return result


@router.post("", response_model=CollectionOut, status_code=201)
def create_collection(
    body: CollectionCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    collection = Collection(
        name=body.name,
        description=body.description,
        color=body.color,
    )
    db.add(collection)
    db.commit()
    db.refresh(collection)
    return CollectionOut(
        id=collection.id,
        name=collection.name,
        description=collection.description,
        color=collection.color,
        created_at=collection.created_at,
        document_count=0,
    )


@router.get("/{collection_id}", response_model=CollectionDetail)
def get_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    collection = db.get(Collection, collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found.")

    docs = (
        db.query(Document)
        .join(DocumentCollection, DocumentCollection.document_id == Document.id)
        .filter(DocumentCollection.collection_id == collection_id)
        .all()
    )

    return CollectionDetail(
        id=collection.id,
        name=collection.name,
        description=collection.description,
        color=collection.color,
        created_at=collection.created_at,
        documents=[{"id": d.id, "title": d.title or d.filename, "filename": d.filename} for d in docs],
    )


@router.delete("/{collection_id}")
def delete_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    collection = db.get(Collection, collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found.")

    db.query(DocumentCollection).filter(DocumentCollection.collection_id == collection_id).delete()
    db.delete(collection)
    db.commit()
    return {"detail": "Collection deleted."}


@router.post("/{collection_id}/documents/{document_id}")
def add_document_to_collection(
    collection_id: int,
    document_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    collection = db.get(Collection, collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found.")

    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")

    existing = (
        db.query(DocumentCollection)
        .filter(
            DocumentCollection.collection_id == collection_id,
            DocumentCollection.document_id == document_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Document already in collection.")

    link = DocumentCollection(document_id=document_id, collection_id=collection_id)
    db.add(link)
    db.commit()
    return {"detail": "Document added to collection."}


@router.delete("/{collection_id}/documents/{document_id}")
def remove_document_from_collection(
    collection_id: int,
    document_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    link = (
        db.query(DocumentCollection)
        .filter(
            DocumentCollection.collection_id == collection_id,
            DocumentCollection.document_id == document_id,
        )
        .first()
    )
    if not link:
        raise HTTPException(status_code=404, detail="Document not in collection.")

    db.delete(link)
    db.commit()
    return {"detail": "Document removed from collection."}
