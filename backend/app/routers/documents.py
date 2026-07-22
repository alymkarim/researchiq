from pathlib import Path
from uuid import uuid4

import fitz
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db


router = APIRouter(
    prefix="/api/documents",
    tags=["documents"],
)

UPLOAD_DIRECTORY = Path("uploads")
UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)


def clean_text(value: str | None) -> str | None:
    """
    Remove characters that PostgreSQL cannot store, including NUL bytes.
    """
    if value is None:
        return None

    return value.replace("\x00", "").strip()


def extract_pdf_content(file_path: Path) -> dict[str, str | None]:
    """
    Extract text and basic metadata from a PDF using PyMuPDF.
    """
    try:
        with fitz.open(file_path) as pdf:
            metadata = pdf.metadata or {}

            page_text = [
                page.get_text("text")
                for page in pdf
            ]

            full_text = clean_text("\n".join(page_text)) or ""

            title = clean_text(metadata.get("title"))
            authors = clean_text(metadata.get("author"))
            subject = clean_text(metadata.get("subject"))

            # Use the first useful line when the PDF has no title metadata.
            if not title and full_text:
                meaningful_lines = [
                    line.strip()
                    for line in full_text.splitlines()
                    if line.strip()
                ]

                if meaningful_lines:
                    title = clean_text(meaningful_lines[0][:500])

            return {
                "title": title,
                "authors": authors,
                "abstract": subject,
                "content": full_text,
            }

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not process PDF: {exc}",
        ) from exc


def build_document_values(
    filename: str,
    stored_path: Path,
    extracted: dict[str, str | None],
) -> dict:
    """
    Build values using only columns that exist in the Document model.

    This supports common text field names such as:
    content, text, full_text and extracted_text.
    """
    document_columns = {
        column.name
        for column in models.Document.__table__.columns
    }

    values: dict = {}

    possible_values = {
        "filename": clean_text(filename),
        "file_path": str(stored_path),
        "filepath": str(stored_path),
        "path": str(stored_path),
        "title": extracted.get("title"),
        "authors": extracted.get("authors"),
        "author": extracted.get("authors"),
        "abstract": extracted.get("abstract"),
        "content": extracted.get("content"),
        "text": extracted.get("content"),
        "full_text": extracted.get("content"),
        "extracted_text": extracted.get("content"),
    }

    for field_name, value in possible_values.items():
        if field_name in document_columns:
            values[field_name] = clean_text(value)

    return values


@router.get(
    "",
    response_model=list[schemas.DocumentOut],
)
def get_documents(
    db: Session = Depends(get_db),
):
    return (
        db.query(models.Document)
        .order_by(models.Document.id.desc())
        .all()
    )


@router.get(
    "/{document_id}",
    response_model=schemas.DocumentOut,
)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(models.Document)
        .filter(models.Document.id == document_id)
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    return document


@router.post(
    "/upload",
    response_model=list[schemas.DocumentOut],
    status_code=status.HTTP_201_CREATED,
)
async def upload_documents(
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one PDF file is required.",
        )

    created_documents: list[models.Document] = []
    saved_paths: list[Path] = []

    try:
        for uploaded_file in files:
            original_filename = clean_text(uploaded_file.filename)

            if not original_filename:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Uploaded file has no filename.",
                )

            is_pdf_name = original_filename.lower().endswith(".pdf")
            is_pdf_type = uploaded_file.content_type == "application/pdf"

            if not is_pdf_name and not is_pdf_type:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{original_filename} is not a PDF file.",
                )

            unique_filename = f"{uuid4().hex}_{Path(original_filename).name}"
            stored_path = UPLOAD_DIRECTORY / unique_filename

            file_bytes = await uploaded_file.read()

            if not file_bytes:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{original_filename} is empty.",
                )

            stored_path.write_bytes(file_bytes)
            saved_paths.append(stored_path)

            extracted = extract_pdf_content(stored_path)

            document_values = build_document_values(
                filename=original_filename,
                stored_path=stored_path,
                extracted=extracted,
            )

            document = models.Document(**document_values)

            db.add(document)
            created_documents.append(document)

        db.commit()

        for document in created_documents:
            db.refresh(document)

        return created_documents

    except HTTPException:
        db.rollback()

        for saved_path in saved_paths:
            saved_path.unlink(missing_ok=True)

        raise

    except Exception as exc:
        db.rollback()

        for saved_path in saved_paths:
            saved_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {exc}",
        ) from exc

    finally:
        for uploaded_file in files:
            await uploaded_file.close()


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(models.Document)
        .filter(models.Document.id == document_id)
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    possible_path_fields = ["file_path", "filepath", "path"]

    stored_path: Path | None = None

    for field_name in possible_path_fields:
        path_value = getattr(document, field_name, None)

        if path_value:
            stored_path = Path(path_value)
            break

    try:
        db.delete(document)
        db.commit()

        if stored_path:
            stored_path.unlink(missing_ok=True)

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {exc}",
        ) from exc

    return None