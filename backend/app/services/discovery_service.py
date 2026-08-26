import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1"
ARXIV_API = "http://export.arxiv.org/api/query"


async def search_semantic_scholar(
    query: str,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Search papers using Semantic Scholar API."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{SEMANTIC_SCHOLAR_API}/paper/search",
                params={
                    "query": query,
                    "limit": limit,
                    "fields": "title,authors,abstract,year,url,externalIds,citationCount",
                },
            )
            response.raise_for_status()
            data = response.json()

        papers = []
        for paper in data.get("data", []):
            authors = [a.get("name", "") for a in paper.get("authors", [])]
            papers.append({
                "title": paper.get("title", ""),
                "authors": ", ".join(authors),
                "abstract": paper.get("abstract", ""),
                "year": paper.get("year"),
                "url": paper.get("url", ""),
                "doi": paper.get("externalIds", {}).get("DOI"),
                "arxiv_id": paper.get("externalIds", {}).get("ArXiv"),
                "citation_count": paper.get("citationCount", 0),
                "source": "semantic_scholar",
            })

        return papers

    except Exception as exc:
        logger.warning("Semantic Scholar search failed: %s", exc)
        return []


async def search_arxiv(
    query: str,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Search papers using arXiv API."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                ARXIV_API,
                params={
                    "search_query": f"all:{query}",
                    "start": 0,
                    "max_results": limit,
                    "sortBy": "relevance",
                    "sortOrder": "descending",
                },
            )
            response.raise_for_status()

        import xml.etree.ElementTree as ET
        root = ET.fromstring(response.text)

        ns = {"atom": "http://www.w3.org/2005/Atom"}
        papers = []

        for entry in root.findall("atom:entry", ns):
            title = entry.find("atom:title", ns)
            summary = entry.find("atom:summary", ns)
            published = entry.find("atom:published", ns)

            authors = []
            for author in entry.findall("atom:author", ns):
                name = author.find("atom:name", ns)
                if name is not None:
                    authors.append(name.text)

            links = entry.findall("atom:link", ns)
            pdf_url = ""
            for link in links:
                if link.get("title") == "pdf":
                    pdf_url = link.get("href", "")

            arxiv_id = ""
            id_elem = entry.find("atom:id", ns)
            if id_elem is not None and id_elem.text:
                arxiv_id = id_elem.text.split("/abs/")[-1] if "/abs/" in id_elem.text else ""

            year = None
            if published is not None and published.text:
                try:
                    year = int(published.text[:4])
                except ValueError:
                    pass

            papers.append({
                "title": title.text.strip().replace("\n", " ") if title is not None and title.text else "",
                "authors": ", ".join(authors),
                "abstract": summary.text.strip().replace("\n", " ") if summary is not None and summary.text else "",
                "year": year,
                "url": f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else "",
                "pdf_url": pdf_url,
                "arxiv_id": arxiv_id,
                "source": "arxiv",
            })

        return papers

    except Exception as exc:
        logger.warning("arXiv search failed: %s", exc)
        return []


async def search_papers(
    query: str,
    sources: list[str] | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Search papers across multiple sources."""
    if sources is None:
        sources = ["semantic_scholar", "arxiv"]

    all_papers = []

    if "semantic_scholar" in sources:
        papers = await search_semantic_scholar(query, limit)
        all_papers.extend(papers)

    if "arxiv" in sources:
        papers = await search_arxiv(query, limit)
        all_papers.extend(papers)

    seen_titles = set()
    unique_papers = []
    for paper in all_papers:
        title_lower = paper["title"].lower().strip()
        if title_lower and title_lower not in seen_titles:
            seen_titles.add(title_lower)
            unique_papers.append(paper)

    return unique_papers[:limit]
