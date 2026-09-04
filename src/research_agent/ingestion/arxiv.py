"""Async arXiv metadata / PDF fetching."""
import re
import aiohttp
import xml.etree.ElementTree as ET
from typing import Optional


ARXIV_API_URL = "https://export.arxiv.org/api/query"
ARXIV_PDF_URL = "https://arxiv.org/pdf"


def extract_arxiv_id(url: str) -> str:
    """Extract arXiv ID from a URL or return as-is if already an ID."""
    # Handle https://arxiv.org/abs/2501.06425 or https://arxiv.org/pdf/2501.06425
    m = re.search(r"arxiv\.org/(?:abs|pdf)/(\d+\.\d+|[a-z-]+/\d+)", url, re.I)
    if m:
        return m.group(1)
    # If it looks like a bare ID, return it
    if re.match(r"^(\d+\.\d+|[a-z-]+/\d+)$", url.strip()):
        return url.strip()
    raise ValueError(f"Could not extract arXiv ID from: {url}")


async def fetch_arxiv_entry(arxiv_id: str) -> Optional[dict]:
    """Fetch a single arXiv entry by ID via the Atom API."""
    params = {"id_list": arxiv_id}
    async with aiohttp.ClientSession() as client:
        async with client.get(ARXIV_API_URL, params=params) as resp:
            resp.raise_for_status()
            xml_text = await resp.text()

    root = ET.fromstring(xml_text)
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }

    entry = root.find("atom:entry", ns)
    if entry is None:
        return None

    def _text(path):
        node = entry.find(path, ns)
        return node.text.strip() if node is not None and node.text else None

    # Find PDF link
    pdf_url = None
    for link in entry.findall("atom:link", ns):
        if link.get("title") == "pdf" or link.get("type") == "application/pdf":
            pdf_url = link.get("href")
            break
    if pdf_url is None:
        pdf_url = f"{ARXIV_PDF_URL}/{arxiv_id}.pdf"

    return {
        "arxiv_id": arxiv_id,
        "title": _text("atom:title"),
        "summary": _text("atom:summary"),
        "published": _text("atom:published"),
        "authors": [
            name.text
            for author in entry.findall("atom:author", ns)
            if (name := author.find("atom:name", ns)) is not None and name.text
        ],
        "pdf_url": pdf_url,
    }


async def download_pdf(url: str) -> bytes:
    """Download PDF bytes from a URL."""
    async with aiohttp.ClientSession() as client:
        async with client.get(url) as resp:
            resp.raise_for_status()
            return await resp.read()
