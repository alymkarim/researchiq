from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..models import Document
from ..schemas import ComparisonOut, ComparisonRequest

router = APIRouter(
    prefix="/api/comparison",
    tags=["comparison"],
)


@router.post("/", response_model=ComparisonOut)
def compare_documents(
    request: ComparisonRequest,
    db: Session = Depends(get_db),
) -> ComparisonOut:
    documents = (
        db.query(Document)
        .options(selectinload(Document.analysis))
        .filter(Document.id.in_(request.document_ids))
        .all()
    )

    if len(documents) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least two valid documents are required.",
        )

    analyses = [
        document.analysis
        for document in documents
        if document.analysis is not None
    ]

    if not analyses:
        return ComparisonOut(documents=documents)

    return ComparisonOut(
        documents=documents,
        objective=_combine_field(analyses, "objective"),
        methodology=_combine_field(analyses, "methodology"),
        dataset=_combine_field(analyses, "dataset"),
        findings=_combine_field(analyses, "findings"),
        strengths=_combine_field(analyses, "strengths"),
        limitations=_combine_field(analyses, "limitations"),
    )


def _combine_field(analyses: list, field_name: str) -> str | None:
    values: list[str] = []

    for analysis in analyses:
        value = getattr(analysis, field_name, None)

        if value and value.strip():
            values.append(value.strip())

    if not values:
        return None

    return "\n\n".join(
        f"Paper {index}: {value}"
        for index, value in enumerate(values, start=1)
    )