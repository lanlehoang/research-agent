"""CLI entry point for batch operations."""
import asyncio
import typer
from rich import print as rprint
from research_agent.storage.database import AsyncSessionLocal
from research_agent.ingestion.pipeline import ingest_arxiv

app = typer.Typer()


@app.command()
def ingest(arxiv_url: str = typer.Argument(..., help="arXiv URL or ID to ingest")):
    """Ingest a single arXiv paper into PostgreSQL."""

    async def _run():
        async with AsyncSessionLocal() as session:
            doc_id = await ingest_arxiv(arxiv_url, session)
            rprint(f"[green]Ingested[/green]: {doc_id}")

    asyncio.run(_run())


if __name__ == "__main__":
    app()
