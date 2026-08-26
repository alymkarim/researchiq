import logging
from typing import Any

from ..utils.text import clean_text

logger = logging.getLogger(__name__)


def find_highlight_positions(
    page_text: str,
    search_terms: list[str],
) -> list[dict[str, Any]]:
    """Find positions of search terms in page text for highlighting."""
    positions = []
    page_lower = page_text.lower()

    for term in search_terms:
        term_lower = term.lower()
        start = 0

        while True:
            index = page_lower.find(term_lower, start)
            if index == -1:
                break

            positions.append({
                "term": term,
                "start": index,
                "end": index + len(term),
                "context": page_text[max(0, index - 50) : index + len(term) + 50],
            })

            start = index + 1

    return positions


def map_analysis_to_pages(
    analysis: dict[str, Any],
    pages: list[dict],
) -> dict[int, list[dict]]:
    """Map analysis findings to specific pages."""
    page_map: dict[int, list[dict]] = {}

    search_fields = [
        ("objective", ["aim", "objective", "purpose", "goal"]),
        ("methodology", ["method", "approach", "procedure", "technique"]),
        ("findings", ["result", "finding", "showed", "demonstrated"]),
        ("limitations", ["limitation", "weakness", "constraint"]),
    ]

    for field, keywords in search_fields:
        content = analysis.get(field, "")
        if not content or content == "Not clearly stated":
            continue

        content_words = set(content.lower().split())
        significant_words = [w for w in content_words if len(w) > 5]

        for page in pages:
            page_text = page.get("text", "")
            page_number = page.get("page", 1)

            matches = []
            for word in significant_words[:10]:
                if word in page_text.lower():
                    matches.append(word)

            if len(matches) >= 2:
                if page_number not in page_map:
                    page_map[page_number] = []

                page_map[page_number].append({
                    "field": field,
                    "matches": matches,
                    "preview": content[:200],
                })

    return page_map


def get_page_references(
    document_text: str,
    analysis: dict[str, Any],
) -> list[dict[str, Any]]:
    """Get page references for analysis results."""
    references = []

    keywords = analysis.get("keywords", "")
    if keywords and keywords != "Not clearly stated":
        keyword_list = [k.strip() for k in keywords.split(",")]
    else:
        keyword_list = []

    objective = analysis.get("objective", "")
    if objective and objective != "Not clearly stated":
        references.append({
            "field": "objective",
            "text": objective[:300],
            "search_terms": keyword_list[:5],
        })

    findings = analysis.get("findings", "")
    if findings and findings != "Not clearly stated":
        references.append({
            "field": "findings",
            "text": findings[:300],
            "search_terms": keyword_list[:5],
        })

    return references
