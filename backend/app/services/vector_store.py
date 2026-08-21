import json
import logging
from pathlib import Path
from typing import Any

import faiss
import numpy as np

from ..config import settings

logger = logging.getLogger(__name__)

INDEX_DIR = Path("vector_indices")
INDEX_DIR.mkdir(exist_ok=True)


def _get_embedding(text: str) -> list[float] | None:
    """Get embedding from OpenAI-compatible API."""
    import httpx

    if not settings.llm_api_key:
        return None

    endpoint = f"{settings.llm_base_url.rstrip('/')}/embeddings"
    model = getattr(settings, "embedding_model", "text-embedding-3-small")

    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(
                endpoint,
                headers={
                    "Authorization": f"Bearer {settings.llm_api_key}",
                    "Content-Type": "application/json",
                },
                json={"model": model, "input": text},
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]
    except Exception as exc:
        logger.warning("Embedding failed: %s", exc)
        return None


def _get_embeddings_batch(texts: list[str]) -> list[list[float]] | None:
    """Get embeddings for multiple texts in one API call."""
    import httpx

    if not settings.llm_api_key:
        return None

    endpoint = f"{settings.llm_base_url.rstrip('/')}/embeddings"
    model = getattr(settings, "embedding_model", "text-embedding-3-small")

    try:
        with httpx.Client(timeout=60) as client:
            response = client.post(
                endpoint,
                headers={
                    "Authorization": f"Bearer {settings.llm_api_key}",
                    "Content-Type": "application/json",
                },
                json={"model": model, "input": texts},
            )
            response.raise_for_status()
            data = response.json()
            return [item["embedding"] for item in data["data"]]
    except Exception as exc:
        logger.warning("Batch embedding failed: %s", exc)
        return None


class VectorIndex:
    """FAISS-based vector index for a single document."""

    def __init__(self, document_id: int):
        self.document_id = document_id
        self.index_path = INDEX_DIR / f"doc_{document_id}.index"
        self.meta_path = INDEX_DIR / f"doc_{document_id}.json"
        self.index: faiss.IndexFlatIP | None = None
        self.metadata: list[dict] = []

    def load(self) -> bool:
        if not self.index_path.exists() or not self.meta_path.exists():
            return False
        try:
            self.index = faiss.read_index(str(self.index_path))
            with open(self.meta_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
            return True
        except Exception as exc:
            logger.warning("Failed to load index for doc %d: %s", self.document_id, exc)
            return False

    def save(self):
        if self.index is not None:
            faiss.write_index(self.index, str(self.index_path))
            with open(self.meta_path, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f)

    def build(self, chunks: list[dict]) -> bool:
        """Build index from chunks: [{"text": str, "page": int, "chunk_index": int}]."""
        texts = [c["text"] for c in chunks]
        embeddings = _get_embeddings_batch(texts)

        if not embeddings:
            return False

        vectors = np.array(embeddings, dtype=np.float32)
        faiss.normalize_L2(vectors)

        dim = vectors.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(vectors)
        self.metadata = [
            {"page": c["page"], "chunk_index": c["chunk_index"], "text": c["text"][:1000]}
            for c in chunks
        ]
        self.save()
        return True

    def search(self, query: str, limit: int = 5) -> list[dict]:
        if self.index is None or self.index.ntotal == 0:
            return []

        embedding = _get_embedding(query)
        if not embedding:
            return []

        query_vector = np.array([embedding], dtype=np.float32)
        faiss.normalize_L2(query_vector)

        k = min(limit, self.index.ntotal)
        scores, indices = self.index.search(query_vector, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue
            meta = self.metadata[idx]
            results.append({
                "document_id": self.document_id,
                "page": meta["page"],
                "text": meta["text"],
                "score": round(float(score), 4),
            })
        return results


def get_or_build_index(document_id: int, chunks: list[dict]) -> VectorIndex:
    """Get existing index or build a new one."""
    index = VectorIndex(document_id)
    if index.load():
        return index
    index.build(chunks)
    return index


def delete_index(document_id: int):
    """Delete index files for a document."""
    idx_path = INDEX_DIR / f"doc_{document_id}.index"
    meta_path = INDEX_DIR / f"doc_{document_id}.json"
    idx_path.unlink(missing_ok=True)
    meta_path.unlink(missing_ok=True)
