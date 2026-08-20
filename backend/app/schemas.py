from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# =========================================================
# ANALYSIS
# =========================================================

class AnalysisOut(BaseModel):
    id: int
    document_id: int

    summary: str | None = None
    objective: str | None = None
    methodology: str | None = None
    dataset: str | None = None
    findings: str | None = None

    # These are stored as strings in the current database model.
    strengths: str | None = None
    limitations: str | None = None
    keywords: str | None = None

    analysis_mode: str | None = None

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# DOCUMENTS
# =========================================================

class DocumentOut(BaseModel):
    id: int
    filename: str
    title: str | None = None
    authors: str | None = None
    abstract: str | None = None
    created_at: datetime | None = None
    analysis: AnalysisOut | None = None

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# SEARCH
# =========================================================

class SearchRequest(BaseModel):
    query: str = Field(
        min_length=2,
        max_length=300,
    )

    document_ids: list[int] = Field(
        default_factory=list,
    )

    limit: int = Field(
        default=5,
        ge=1,
        le=20,
    )


class SearchResultOut(BaseModel):
    document_id: int
    document_title: str
    filename: str
    page: int | None = None
    text: str
    score: float


# Backwards-compatible name expected by the existing search router.
SearchResult = SearchResultOut


# =========================================================
# COMPARISON
# =========================================================

class ComparisonRequest(BaseModel):
    document_ids: list[int] = Field(
        min_length=2,
        max_length=10,
    )


# Backwards-compatible name expected by some comparison routers.
CompareRequest = ComparisonRequest


class ComparisonPaper(BaseModel):
    document_id: int
    title: str
    filename: str | None = None

    summary: str | None = None
    objective: str | None = None
    methodology: str | None = None
    dataset: str | None = None
    findings: str | None = None

    strengths: str | None = None
    limitations: str | None = None
    keywords: str | None = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedDocuments(BaseModel):
    items: list[DocumentOut]
    total: int
    page: int
    per_page: int
    pages: int


class ComparisonOut(BaseModel):
    # Supports the original comparison response.
    documents: list[DocumentOut] = Field(
        default_factory=list,
    )

    objective: str | None = None
    methodology: str | None = None
    dataset: str | None = None
    findings: str | None = None
    strengths: str | None = None
    limitations: str | None = None

    # Supports the newer comparison router if it returns individual papers.
    papers: list[ComparisonPaper] = Field(
        default_factory=list,
    )

    shared_keywords: list[str] = Field(
        default_factory=list,
    )

    similarities: list[str] = Field(
        default_factory=list,
    )

    differences: list[str] = Field(
        default_factory=list,
    )