from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def chunk_text(text: str, size: int = 1000, overlap: int = 150) -> list[str]:
    text = " ".join(text.split())
    chunks = []
    start = 0

    while start < len(text):
        end = min(start + size, len(text))
        chunks.append(text[start:end])

        if end == len(text):
            break

        start = end - overlap

    return chunks


def search_documents(documents, query: str, limit: int) -> list[dict]:
    records = []

    for document in documents:
        if not document.full_text:
            continue

        for chunk in chunk_text(document.full_text):
            records.append(
                {
                    "document_id": document.id,
                    "title": document.title or document.filename,
                    "filename": document.filename,
                    "chunk": chunk,
                }
            )

    if not records:
        return []

    corpus = [record["chunk"] for record in records]

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=7000,
    )

    matrix = vectorizer.fit_transform(corpus + [query])
    scores = cosine_similarity(matrix[-1], matrix[:-1]).flatten()

    results = []
    seen = set()

    for index in scores.argsort()[::-1]:
        record = records[index]
        score = float(scores[index])

        if score <= 0:
            continue

        if record["document_id"] in seen:
            continue

        results.append(
            {
                "document_id": record["document_id"],
                "document_title": record["title"],
                "filename": record["filename"],
                "text": record["chunk"][:700],
                "score": round(score, 4),
            }
        )

        seen.add(record["document_id"])

        if len(results) >= limit:
            break

    return results