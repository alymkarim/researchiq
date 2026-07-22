from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class AnalysisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_id: int
    objective: str
    methodology: str
    dataset: str
    findings: str
    strengths: str
    limitations: str
    keywords: str
    created_at: datetime

class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    filename: str
    title: str | None
    authors: str | None
    abstract: str | None
    created_at: datetime
    analysis: AnalysisOut | None = None

class SearchRequest(BaseModel):
    query: str = Field(min_length=2)
    limit: int = Field(default=5, ge=1, le=20)

class SearchResult(BaseModel):
    document_id: int
    document_title: str
    filename: str
    text: str
    score: float

class CompareRequest(BaseModel):
    document_ids: list[int] = Field(min_length=2, max_length=5)

class ComparisonPaper(BaseModel):
    document_id: int
    title: str
    objective: str
    methodology: str
    dataset: str
    findings: str
    limitations: str

class ComparisonOut(BaseModel):
    papers: list[ComparisonPaper]
    common_keywords: list[str]
    summary: str
