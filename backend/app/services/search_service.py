import json
import logging
import re
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ..utils.text import clean_text
from .vector_store import VectorIndex, get_or_build_index

logger = logging.getLogger(__name__)

# TODO: experiment with different chunk sizes, 1000 feels arbitrary
def chunk_text(
    text: str,
    size: int = 1000,
    overlap: int = 150,
) -> list[str]:
    text = clean_text(text)

    if not text:
        return []

    chunks: list[str] = []
    start = 0

    while start < len(text):
        end = min(start + size, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break

        start = max(0, end - overlap)

    return chunks


def get_document_pages(document: Any) -> list[dict]:
    pages_json = getattr(document, "pages_json", None)

    if pages_json:
        try:
            pages = json.loads(pages_json)

            if isinstance(pages, list):
                valid_pages = []

                for page in pages:
                    if not isinstance(page, dict):
                        continue

                    text = clean_text(str(page.get("text", "")))

                    if not text:
                        continue

                    valid_pages.append(
                        {
                            "page": int(page.get("page", 1)),
                            "text": text,
                        }
                    )

                if valid_pages:
                    return valid_pages

        except (json.JSONDecodeError, TypeError, ValueError):
            pass

    # Fallback for PDFs uploaded before pages_json was added.
    return [
        {
            "page": 1,
            "text": clean_text(getattr(document, "full_text", "")),
        }
    ]


def _build_chunks_for_document(document: Any) -> list[dict]:
    """Build chunk list with metadata for a document."""
    chunks = []
    chunk_index = 0

    for page_data in get_document_pages(document):
        page_number = page_data["page"]
        for text in chunk_text(page_data["text"]):
            chunks.append({
                "text": text,
                "page": page_number,
                "chunk_index": chunk_index,
            })
            chunk_index += 1

    return chunks


def _vector_search(documents, query: str, limit: int) -> list[dict] | None:
    """Try vector-based search. Returns None if embeddings unavailable."""
    all_results = []

    for document in documents:
        chunks = _build_chunks_for_document(document)
        if not chunks:
            continue

        index = get_or_build_index(document.id, chunks)
        results = index.search(query, limit=limit)

        for r in results:
            r["document_title"] = document.title or document.filename
            r["filename"] = document.filename

        all_results.extend(results)

    if not all_results:
        return None

    all_results.sort(key=lambda x: x["score"], reverse=True)

    seen: set[tuple[int, int]] = set()
    filtered = []
    for r in all_results:
        key = (r["document_id"], r["page"])
        if key not in seen:
            seen.add(key)
            filtered.append(r)
        if len(filtered) >= limit:
            break

    return filtered


def _tfidf_search(documents, query: str, limit: int) -> list[dict]:
    """Fallback TF-IDF search."""
    cleaned_query = clean_text(query)

    if not cleaned_query:
        return []

    records: list[dict] = []

    for document in documents:
        title = document.title or document.filename

        for page_data in get_document_pages(document):
            page_number = page_data["page"]

            for chunk in chunk_text(page_data["text"]):
                records.append(
                    {
                        "document_id": document.id,
                        "document_title": title,
                        "filename": document.filename,
                        "page": page_number,
                        "chunk": chunk,
                    }
                )

    if not records:
        return []

    corpus = [record["chunk"] for record in records]

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=7000,
        ngram_range=(1, 2),
    )

    try:
        matrix = vectorizer.fit_transform(corpus + [cleaned_query])
    except ValueError:
        return []

    scores = cosine_similarity(
        matrix[-1],
        matrix[:-1],
    ).flatten()

    ranked_indices = scores.argsort()[::-1]

    results: list[dict] = []
    seen: set[tuple[int, int]] = set()

    for index in ranked_indices:
        score = float(scores[index])

        if score <= 0:
            continue

        record = records[index]

        unique_key = (
            record["document_id"],
            record["page"],
        )

        if unique_key in seen:
            continue

        results.append(
            {
                "document_id": record["document_id"],
                "document_title": record["document_title"],
                "filename": record["filename"],
                "page": record["page"],
                "text": record["chunk"][:700],
                "score": round(score, 4),
            }
        )

        seen.add(unique_key)

        if len(results) >= limit:
            break

    return results


def search_documents(
    documents,
    query: str,
    limit: int,
) -> list[dict]:
    """Search using vector embeddings if available, otherwise TF-IDF."""
    vector_results = _vector_search(documents, query, limit)
    if vector_results is not None:
        return vector_results

    return _tfidf_search(documents, query, limit)
