from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def find_related_documents(target_doc, all_documents, limit=3):
    """Find documents most similar to the target using TF-IDF."""
    docs = [d for d in all_documents if d.id != target_doc.id]
    if not docs:
        return []

    # Limit to 20 documents to prevent OOM
    docs = docs[:20]

    corpus = [target_doc.full_text[:5000]] + [d.full_text[:5000] for d in docs]

    vectorizer = TfidfVectorizer(stop_words="english", max_features=3000)
    matrix = vectorizer.fit_transform(corpus)

    scores = cosine_similarity(matrix[0], matrix[1:]).flatten()
    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)

    results = []
    for idx, score in ranked[:limit]:
        if score > 0.05:
            results.append({
                "document_id": docs[idx].id,
                "title": docs[idx].title or docs[idx].filename,
                "similarity": round(float(score), 4),
            })
    return results
