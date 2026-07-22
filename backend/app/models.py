from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    authors: Mapped[str | None] = mapped_column(String(500), nullable=True)
    abstract: Mapped[str | None] = mapped_column(Text, nullable=True)
    full_text: Mapped[str] = mapped_column(Text)
    file_path: Mapped[str] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    analysis: Mapped["Analysis | None"] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
        uselist=False,
    )

class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        unique=True,
    )

    objective: Mapped[str] = mapped_column(Text, default="")
    methodology: Mapped[str] = mapped_column(Text, default="")
    dataset: Mapped[str] = mapped_column(Text, default="")
    findings: Mapped[str] = mapped_column(Text, default="")
    strengths: Mapped[str] = mapped_column(Text, default="")
    limitations: Mapped[str] = mapped_column(Text, default="")
    keywords: Mapped[str] = mapped_column(Text, default="")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    document: Mapped[Document] = relationship(back_populates="analysis")
