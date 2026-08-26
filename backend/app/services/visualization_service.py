import json
import logging
import re
from collections import Counter
from typing import Any

logger = logging.getLogger(__name__)

STOPWORDS = {
    "the", "and", "for", "that", "with", "this", "from", "were", "was",
    "are", "have", "has", "using", "into", "their", "these", "which",
    "our", "they", "been", "can", "than", "also", "between", "study",
    "paper", "results", "method", "methods", "research", "based",
    "chapter", "book", "introduction", "conclusion", "authors",
    "figure", "table", "section", "page", "references", "et", "al",
}


def generate_word_cloud_data(
    text: str,
    max_words: int = 50,
) -> list[dict[str, Any]]:
    """Generate word cloud data from text."""
    words = re.findall(r"\b[a-zA-Z][a-zA-Z-]{3,}\b", text.lower())
    filtered = [w for w in words if w not in STOPWORDS and len(w) > 3]
    counts = Counter(filtered).most_common(max_words)

    if not counts:
        return []

    max_count = counts[0][1]

    return [
        {
            "text": word,
            "value": count,
            "size": max(12, int(40 * count / max_count)),
        }
        for word, count in counts
    ]


def generate_keyword_network(
    text: str,
    max_nodes: int = 30,
) -> dict[str, Any]:
    """Generate keyword co-occurrence network data."""
    sentences = re.split(r"[.!?]+", text)
    words_per_sentence = []

    for sentence in sentences:
        words = re.findall(r"\b[a-zA-Z][a-zA-Z-]{3,}\b", sentence.lower())
        filtered = [w for w in words if w not in STOPWORDS and len(w) > 3]
        words_per_sentence.append(set(filtered))

    word_counts = Counter()
    for words in words_per_sentence:
        word_counts.update(words)

    top_words = [w for w, _ in word_counts.most_common(max_nodes)]
    top_set = set(top_words)

    co_occurrences = []
    for words in words_per_sentence:
        relevant = words & top_set
        relevant_list = sorted(relevant)

        for i in range(len(relevant_list)):
            for j in range(i + 1, len(relevant_list)):
                co_occurrences.append((relevant_list[i], relevant_list[j]))

    edge_counts = Counter(co_occurrences)

    nodes = [
        {"id": word, "label": word, "size": word_counts[word]}
        for word in top_words
    ]

    edges = [
        {"source": src, "target": tgt, "weight": count}
        for (src, tgt), count in edge_counts.most_common(50)
        if count >= 2
    ]

    return {"nodes": nodes, "edges": edges}


def generate_methodology_timeline(
    analysis: dict[str, Any],
) -> list[dict[str, str]]:
    """Generate methodology timeline from analysis."""
    methodology = analysis.get("methodology", "")
    if not methodology or methodology == "Not clearly stated":
        return []

    steps = re.split(r"[;.]|\band\b", methodology)
    timeline = []

    for i, step in enumerate(steps):
        step = step.strip()
        if len(step) > 10:
            timeline.append({
                "step": i + 1,
                "description": step[:200],
            })

    return timeline


def generate_citation_graph(
    documents: list[dict[str, Any]],
) -> dict[str, Any]:
    """Generate citation relationship graph."""
    nodes = []
    edges = []

    for doc in documents:
        nodes.append({
            "id": doc.get("id"),
            "label": doc.get("title", "Untitled")[:50],
            "year": doc.get("year"),
            "authors": doc.get("authors", ""),
        })

    titles = {doc.get("id"): doc.get("title", "").lower() for doc in documents}

    for i, doc1 in enumerate(documents):
        for j, doc2 in enumerate(documents):
            if i >= j:
                continue

            title1 = titles.get(doc1.get("id"), "")
            title2 = titles.get(doc2.get("id"), "")

            words1 = set(re.findall(r"\b\w{4,}\b", title1))
            words2 = set(re.findall(r"\b\w{4,}\b", title2))

            overlap = words1 & words2
            if len(overlap) >= 2:
                edges.append({
                    "source": doc1.get("id"),
                    "target": doc2.get("id"),
                    "weight": len(overlap),
                    "shared_terms": list(overlap)[:5],
                })

    return {"nodes": nodes, "edges": edges}
