from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    username: Mapped[str] = mapped_column(String(100), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    title: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    authors: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    abstract: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    full_text: Mapped[str] = mapped_column(Text)

    # JSON string containing page numbers and page text.
    pages_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    file_path: Mapped[str] = mapped_column(String(1000))
    
    pdf_content: Mapped[bytes | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    analysis: Mapped["Analysis | None"] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
        uselist=False,
    )


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(primary_key=True)

    document_id: Mapped[int] = mapped_column(
        ForeignKey(
            "documents.id",
            ondelete="CASCADE",
        ),
        unique=True,
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    objective: Mapped[str] = mapped_column(
        Text,
        default="",
    )
    methodology: Mapped[str] = mapped_column(
        Text,
        default="",
    )
    dataset: Mapped[str] = mapped_column(
        Text,
        default="",
    )
    findings: Mapped[str] = mapped_column(
        Text,
        default="",
    )
    strengths: Mapped[str] = mapped_column(
        Text,
        default="",
    )
    limitations: Mapped[str] = mapped_column(
        Text,
        default="",
    )
    keywords: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    analysis_mode: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    document: Mapped[Document] = relationship(
        back_populates="analysis",
    )


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    content: Mapped[str] = mapped_column(Text)
    page_number: Mapped[int | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship()
    document: Mapped["Document"] = relationship()


class Annotation(Base):
    __tablename__ = "annotations"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    page_number: Mapped[int] = mapped_column()
    highlight_text: Mapped[str] = mapped_column(Text)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    color: Mapped[str] = mapped_column(String(20), default="#ffd547")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship()
    document: Mapped["Document"] = relationship()


class Collection(Base):
    __tablename__ = "collections"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    color: Mapped[str] = mapped_column(String(20), default="#6c5ce7")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class DocumentCollection(Base):
    __tablename__ = "document_collections"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    collection_id: Mapped[int] = mapped_column(ForeignKey("collections.id", ondelete="CASCADE"))
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    document: Mapped["Document"] = relationship()
    collection: Mapped["Collection"] = relationship()


class SharedSession(Base):
    __tablename__ = "shared_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    share_id: Mapped[str] = mapped_column(String(20), unique=True)
    title: Mapped[str] = mapped_column(String(500))
    document_ids: Mapped[str] = mapped_column(Text)
    analysis_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )