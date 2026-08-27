"""
Define agent tools
"""
import aiohttp
import xml.etree.ElementTree as ET


async def search_arxiv(query: str, max_results: int = 10):
    """Search arXiv API for a query. Returns parsed Atom XML as structured dict."""
    ARXIV_API_URL = "https://export.arxiv.org/api/query"
    params = {
        "search_query": query,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": max_results,
    }
    try:
        async with aiohttp.ClientSession() as client:
            response = await client.get(ARXIV_API_URL, params=params)
            response.raise_for_status()
            xml_text = await response.text()
    except aiohttp.ClientError as e:
        return {"error": str(e)}

    # Parse Atom XML
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        return {"error": f"XML parse error: {e}"}

    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
        "opensearch": "http://a9.com/-/spec/opensearch/1.1/",
    }

    def _text_or_none(elem, path):
        node = elem.find(path, ns)
        return node.text.strip() if node is not None and node.text else None

    def _int_or_none(elem, path):
        node = elem.find(path, ns)
        return int(node.text) if node is not None and node.text else None

    entries = []
    for entry in root.findall("atom:entry", ns):
        entry_data = {
            "id": _text_or_none(entry, "atom:id"),
            "title": _text_or_none(entry, "atom:title"),
            "summary": _text_or_none(entry, "atom:summary"),
            "published": _text_or_none(entry, "atom:published"),
            "updated": _text_or_none(entry, "atom:updated"),
            "authors": [
                name.text
                for author in entry.findall("atom:author", ns)
                if (name := author.find("atom:name", ns)) is not None and name.text
            ],
            "categories": [
                cat.get("term")
                for cat in entry.findall("atom:category", ns)
                if cat.get("term")
            ],
            "primary_category": (
                entry.find("arxiv:primary_category", ns).get("term")
                if entry.find("arxiv:primary_category", ns) is not None
                else None
            ),
            "comment": _text_or_none(entry, "arxiv:comment"),
            "journal_ref": _text_or_none(entry, "arxiv:journal_ref"),
            "doi": _text_or_none(entry, "arxiv:doi"),
            "links": [
                {
                    "href": link.get("href"),
                    "rel": link.get("rel"),
                    "type": link.get("type"),
                    "title": link.get("title"),
                }
                for link in entry.findall("atom:link", ns)
            ],
        }
        entries.append(entry_data)

    return {
        "total_results": _int_or_none(root, "opensearch:totalResults"),
        "start_index": _int_or_none(root, "opensearch:startIndex"),
        "items_per_page": _int_or_none(root, "opensearch:itemsPerPage"),
        "entries": entries,
    }


async def search_collection(query: str, max_results: int = 10):
    pass