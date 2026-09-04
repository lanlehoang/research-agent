"""Async repository for Articles and Chunks."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Optional
from research_agent.storage.models import Article, Chunk


async def get_article(session: AsyncSession, doc_id: str) -> Optional[Article]:
    """Fetch an article by doc_id."""
    result = await session.execute(select(Article).where(Article.doc_id == doc_id))
    return result.scalar_one_or_none()


async def delete_article(session: AsyncSession, doc_id: str) -> None:
    """Delete an article (chunks cascade)."""
    await session.execute(delete(Article).where(Article.doc_id == doc_id))
    await session.commit()


async def upsert_article(
    session: AsyncSession,
    doc_id: str,
    title: str,
    abstract: str,
    table_of_contents: dict,
    embedding: list,
    published_date,
    chunks_data: list,
) -> Article:
    """Insert or replace an article with its chunks."""
    existing = await get_article(session, doc_id)
    if existing:
        await delete_article(session, doc_id)

    article = Article(
        doc_id=doc_id,
        title=title,
        abstract=abstract,
        table_of_contents=table_of_contents,
        embedding=embedding,
        published_date=published_date,
    )
    session.add(article)

    for ch in chunks_data:
        chunk = Chunk(
            chunk_id=ch["chunk_id"],
            doc_id=doc_id,
            chunk_name=ch["chunk_name"],
            content=ch["content"],
        )
        session.add(chunk)

    await session.commit()
    await session.refresh(article)
    return article
