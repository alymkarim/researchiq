from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..models import Document
from ..schemas import ComparisonOut, ComparisonPaper, ComparisonRequest

router = APIRouter(
    prefix="/api/comparison",
    tags=["comparison"],
)


@router.post("", response_model=ComparisonOut)
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

    missing_analysis = [
        document.title or document.filename
        for document in documents
        if document.analysis is None
    ]

    if missing_analysis:
        raise HTTPException(
            status_code=400,
            detail=(
                "Analyse all selected papers before comparing them. "
                f"Missing analysis: {', '.join(missing_analysis)}"
            ),
        )

    papers = [
        ComparisonPaper(
            document_id=document.id,
            title=document.title or document.filename,
            filename=document.filename,
            summary=document.analysis.summary,
            objective=document.analysis.objective,
            methodology=document.analysis.methodology,
            dataset=document.analysis.dataset,
            findings=document.analysis.findings,
            strengths=document.analysis.strengths,
            limitations=document.analysis.limitations,
            keywords=document.analysis.keywords,
        )
        for document in documents
    ]

    shared_keywords = find_shared_keywords(documents)
    similarities = build_similarities(documents)
    differences = build_differences(documents)

    return ComparisonOut(
        documents=documents,
        papers=papers,
        shared_keywords=shared_keywords,
        similarities=similarities,
        differences=differences,
    )


def parse_keywords(value: str | None) -> set[str]:
    if not value:
        return set()

    return {
        keyword.strip().lower()
        for keyword in value.replace("\n", ",").split(",")
        if keyword.strip()
        and keyword.strip().lower() != "not clearly stated"
    }


def find_shared_keywords(documents: list[Document]) -> list[str]:
    keyword_sets = [
        parse_keywords(document.analysis.keywords)
        for document in documents
        if document.analysis is not None
    ]

    if not keyword_sets:
        return []

    shared = set.intersection(*keyword_sets)

    return sorted(keyword.title() for keyword in shared)


def valid_text(value: str | None) -> bool:
    return bool(
        value
        and value.strip()
        and value.strip().lower() != "not clearly stated"
    )


def build_similarities(documents: list[Document]) -> list[str]:
    similarities: list[str] = []

    fields = {
        "objective": "research objectives",
        "methodology": "methodological approaches",
        "dataset": "datasets or samples",
        "findings": "main findings",
    }

    for field_name, label in fields.items():
        available_values = [
            getattr(document.analysis, field_name, None)
            for document in documents
            if document.analysis is not None
        ]

        valid_values = [
            value for value in available_values if valid_text(value)
        ]

        if len(valid_values) == len(documents):
            similarities.append(
                f"All selected papers provide information about their {label}."
            )

    shared_keywords = find_shared_keywords(documents)

    if shared_keywords:
        similarities.append(
            "The papers share keywords including "
            + ", ".join(shared_keywords[:6])
            + "."
        )

    return similarities


def build_differences(documents: list[Document]) -> list[str]:
    differences: list[str] = []

    fields = {
        "objective": "objective",
        "methodology": "methodology",
        "dataset": "dataset or sample",
        "findings": "findings",
    }

    for field_name, label in fields.items():
        values = []

        for document in documents:
            analysis = document.analysis
            value = getattr(analysis, field_name, None)

            if valid_text(value):
                values.append(
                    f"{document.title or document.filename}: {value}"
                )

        unique_values = {
            value.split(": ", 1)[-1].strip().lower()
            for value in values
        }

        if len(unique_values) > 1:
            differences.append(
                f"The papers differ in their {label}: "
                + " | ".join(values)
            )

    return differences