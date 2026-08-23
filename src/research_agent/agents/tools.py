"""
Define agent tools
"""
import aiohttp


async def search_arxiv(query: str, max_results: int = 10):
    """Search arXiv API for a query"""
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
            return await response.json()
    except aiohttp.ClientError as e:
        return {"error": str(e)}
