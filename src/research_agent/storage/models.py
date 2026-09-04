"""SQLAlchemy ORM models for PostgreSQL."""
from datetime import date
from sqlalchemy import Column, Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, relationship
from pgvector.sqlalchemy import Vector

Base = declarative_base()


class Article(Base):
    __tablename__ = "articles"

    doc_id = Column(String(16), primary_key=True)
    title = Column(Text)
    abstract = Column(Text, nullable=False)
    table_of_contents = Column(JSONB)
    embedding = Column(Vector(1024), nullable=False)
    published_date = Column(Date)

    chunks = relationship(
        "Chunk",
        back_populates="article",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class Chunk(Base):
    __tablename__ = "chunks"

    chunk_id = Column(String(16), primary_key=True)
    doc_id = Column(
        String(16),
        ForeignKey("articles.doc_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_name = Column(Text, nullable=False)
    content = Column(Text, nullable=False)

    article = relationship("Article", back_populates="chunks")
