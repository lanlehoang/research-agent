"""Main ingestion pipeline: arXiv -> chunks -> Postgres."""
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from research_agent.ingestion.arxiv import extract_arxiv_id, fetch_arxiv_entry, download_pdf
from research_agent.file_processor.pdf_to_md import parse_pdf_to_markdown
from research_agent.file_processor.chunking import Chunker
from research_agent.utils.models import Article
from research_agent.storage.repository import upsert_article, get_article
from research_agent.utils.config import settings


async def ingest_arxiv(url: str, session: AsyncSession) -> str:
    """Ingest a single arXiv paper by URL. Returns the doc_id."""
    arxiv_id = extract_arxiv_id(url)

    # Fetch metadata
    meta = await fetch_arxiv_entry(arxiv_id)
    if meta is None:
        raise ValueError(f"arXiv entry not found: {arxiv_id}")

    # Check existing
    existing = await get_article(session, arxiv_id)
    api_date = datetime.strptime(meta["published"], "%Y-%m-%dT%H:%M:%SZ").date()
    if existing and existing.published_date and api_date <= existing.published_date:
        return arxiv_id  # already up to date

    # Download + parse PDF -> markdown
    pdf_bytes = await download_pdf(meta["pdf_url"])
    markdown = parse_pdf_to_markdown(pdf_bytes)

    # Chunking
    article = Article(doc_id=arxiv_id, doc_name=meta["title"], content=markdown)
    chunker = Chunker()
    toc, chunks = chunker.build_chunks(article)

    # Embed abstract (placeholder: replace with actual embedding model call)
    # TODO: replace with real embedding generation via embedding API
    abstract_text = meta["summary"] or ""
    embedding = [0.0] * settings.EMBEDDING_DIM

    # Serialize ToC
    def _serialize_toc(section):
        return {
            "section_id": section.section_id,
            "subsections": [_serialize_toc(sub) for sub in section.subsections],
        }

    toc_json = _serialize_toc(toc)

    # Persist
    chunks_data = [
        {
            "chunk_id": c.chunk_id,
            "chunk_name": c.chunk_name,
            "content": c.content,
        }
        for c in chunks
    ]

    await upsert_article(
        session,
        doc_id=arxiv_id,
        title=meta["title"] or "",
        abstract=abstract_text,
        table_of_contents=toc_json,
        embedding=embedding,
        published_date=api_date,
        chunks_data=chunks_data,
    )

    return arxiv_id
