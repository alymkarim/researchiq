import json
import re
from pathlib import Path
from uuid import uuid4

import fitz
import math

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..models import Document
from ..schemas import DocumentOut, PaginatedDocuments
from ..utils.text import clean_text as clean_extracted_text


router = APIRouter(
    prefix="/api/documents",
    tags=["documents"],
)

UPLOAD_DIRECTORY = Path("uploads")
UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB


def clean_metadata_text(value: str | None) -> str | None:
    cleaned = clean_extracted_text(value)

    if not cleaned:
        return None

    return cleaned


def extract_pdf_pages(file_path: Path) -> list[dict[str, object]]:
    """Extract selectable text from each PDF page."""
    pages: list[dict[str, object]] = []

    with fitz.open(file_path) as pdf:
        for page_index, page in enumerate(pdf):
            page_text = clean_extracted_text(page.get_text("text"))

            if not page_text:
                continue

            pages.append(
                {
                    "page": page_index + 1,
                    "text": page_text,
                }
            )

    return pages


def extract_title(pdf: fitz.Document, fallback: str) -> str:
    """Extract a useful title from metadata or the first page."""
    metadata_title = clean_metadata_text(pdf.metadata.get("title"))

    if metadata_title and len(metadata_title) > 3:
        return metadata_title[:500]

    if len(pdf) > 0:
        first_page = pdf[0]
        blocks = first_page.get_text("blocks")

        candidates: list[tuple[float, str]] = []

        for block in blocks:
            if len(block) < 5:
                continue

            text = clean_extracted_text(str(block[4]))

            if not text:
                continue

            if len(text) < 5 or len(text) > 500:
                continue

            # Prefer text positioned near the top of the first page.
            y_position = float(block[1])
            candidates.append((y_position, text))

        if candidates:
            candidates.sort(key=lambda item: item[0])

            for _, candidate in candidates[:8]:
                lowered = candidate.lower()

                if any(
                    unwanted in lowered
                    for unwanted in (
                        "abstract",
                        "introduction",
                        "copyright",
                        "doi:",
                        "http://",
                        "https://",
                    )
                ):
                    continue

                return candidate[:500]

    return Path(fallback).stem[:500]


def extract_authors(pdf: fitz.Document) -> str | None:
    """Extract authors primarily from PDF metadata."""
    metadata_authors = clean_metadata_text(pdf.metadata.get("author"))

    if metadata_authors:
        return metadata_authors[:500]

    return None


def extract_abstract(full_text: str) -> str | None:
    """Try to extract the abstract section from the paper text."""
    patterns = [
        r"\babstract\b[:\s]*(.*?)(?=\bkeywords?\b|\bintroduction\b|\b1[\.\s]+introduction\b)",
        r"\bsummary\b[:\s]*(.*?)(?=\bkeywords?\b|\bintroduction\b)",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            full_text,
            flags=re.IGNORECASE | re.DOTALL,
        )

        if not match:
            continue

        abstract = clean_extracted_text(match.group(1))

        if 40 <= len(abstract):
            return abstract[:3000]

    return None


def validate_pdf_upload(file: UploadFile) -> None:
    filename = file.filename or ""

    is_pdf_name = filename.lower().endswith(".pdf")
    is_pdf_type = file.content_type in {
        "application/pdf",
        "application/x-pdf",
        "application/octet-stream",
    }

    if not is_pdf_name or not is_pdf_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported.",
        )


async def save_uploaded_pdf(
    file: UploadFile,
) -> tuple[Path, str, bytes]:
    validate_pdf_upload(file)

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded PDF is empty.",
        )

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Each PDF must be smaller than 15 MB.",
        )

    original_filename = Path(file.filename or "paper.pdf").name
    stored_filename = f"{uuid4().hex}.pdf"
    saved_path = UPLOAD_DIRECTORY / stored_filename

    saved_path.write_bytes(file_bytes)

    return saved_path, original_filename, file_bytes


def build_document_from_pdf(
    file_path: Path,
    original_filename: str,
) -> Document:
    try:
        pages = extract_pdf_pages(file_path)

        if not pages:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"No selectable text was found in {original_filename}. "
                    "The PDF may be scanned and require OCR."
                ),
            )

        full_text = "\n\n".join(
            str(page["text"])
            for page in pages
        )

        with fitz.open(file_path) as pdf:
            title = extract_title(pdf, original_filename)
            authors = extract_authors(pdf)

        abstract = extract_abstract(full_text)

        return Document(
            filename=original_filename,
            title=title,
            authors=authors,
            abstract=abstract,
            full_text=full_text,
            pages_json=json.dumps(
                pages,
                ensure_ascii=False,
            ),
            file_path=str(file_path),
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"{original_filename} could not be read as a valid PDF."
            ),
        ) from exc


@router.get(
    "",
    response_model=PaginatedDocuments,
)
def get_documents(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PaginatedDocuments:
    total = db.scalar(select(func.count(Document.id)))
    total = total or 0
    pages = max(1, math.ceil(total / per_page))
    offset = (page - 1) * per_page

    statement = (
        select(Document)
        .options(selectinload(Document.analysis))
        .order_by(Document.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )

    items = list(db.scalars(statement).all())

    return PaginatedDocuments(
        items=[DocumentOut.model_validate(d) for d in items],
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )


@router.get(
    "/{document_id}",
    response_model=DocumentOut,
)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
) -> Document:
    statement = (
        select(Document)
        .options(selectinload(Document.analysis))
        .where(Document.id == document_id)
    )

    document = db.scalar(statement)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    return document


@router.get("/{document_id}/pdf")
def get_document_pdf(
    document_id: int,
    db: Session = Depends(get_db),
) -> FileResponse:
    document = db.get(Document, document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    file_path = Path(document.file_path)

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF file not found.",
        )

    return FileResponse(file_path, media_type="application/pdf")


@router.post(
    "/upload",
    response_model=list[DocumentOut],
    status_code=status.HTTP_201_CREATED,
)
async def upload_documents(
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
) -> list[Document]:
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please select at least one PDF.",
        )

    saved_paths: list[Path] = []
    created_documents: list[Document] = []

    try:
        for file in files:
            saved_path, original_filename, _ = await save_uploaded_pdf(file)
            saved_paths.append(saved_path)

            document = build_document_from_pdf(
                file_path=saved_path,
                original_filename=original_filename,
            )

            db.add(document)
            created_documents.append(document)

        db.commit()

        for document in created_documents:
            db.refresh(document)

        return created_documents

    except HTTPException:
        db.rollback()

        for path in saved_paths:
            path.unlink(missing_ok=True)

        raise

    except Exception as exc:
        db.rollback()

        for path in saved_paths:
            path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The documents could not be saved.",
        ) from exc

    finally:
        for file in files:
            await file.close()


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
) -> None:
    document = db.get(Document, document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    file_path = Path(document.file_path)

    try:
        db.delete(document)
        db.commit()
    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The document could not be deleted.",
        ) from exc

    file_path.unlink(missing_ok=True)