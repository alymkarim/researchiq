import logging
from typing import Any

from ..services.analysis_service import analyse_document

logger = logging.getLogger(__name__)


async def batch_analyse(
    documents: list[Any],
) -> list[dict[str, Any]]:
    """Analyse multiple documents."""
    results = []

    for document in documents:
        try:
            text = document.full_text or ""
            title = document.title or document.filename
            analysis = await analyse_document(text, title)
            results.append({
                "document_id": document.id,
                "title": title,
                "analysis": analysis,
                "status": "success",
            })
        except Exception as exc:
            logger.exception("Batch analysis failed for doc %d: %s", document.id, exc)
            results.append({
                "document_id": document.id,
                "title": document.title or document.filename,
                "analysis": None,
                "status": "error",
                "error": str(exc),
            })

    return results
