import logging
from typing import Any

import httpx

from ..config import settings
from ..utils.text import clean_text
from .search_service import chunk_text, get_document_pages

logger = logging.getLogger(__name__)

MAX_CONTEXT_CHUNKS = 5
MAX_HISTORY_MESSAGES = 10

# TODO: this is kinda hacky, should probably use embeddings for better retrieval
def _get_relevant_context(document, question: str) -> str:
    """Get relevant chunks from the document for the question."""
    chunks = []

    for page_data in get_document_pages(document):
        page_number = page_data["page"]
        for text in chunk_text(page_data["text"]):
            chunks.append({"text": text, "page": page_number})

    if not chunks:
        return ""

    question_lower = question.lower()
    scored = []

    for chunk in chunks:
        text_lower = chunk["text"].lower()
        words = set(question_lower.split())
        overlap = sum(1 for w in words if w in text_lower)
        scored.append((overlap, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)

    context_parts = []
    for _, chunk in scored[:MAX_CONTEXT_CHUNKS]:
        context_parts.append(f"[Page {chunk['page']}]: {chunk['text'][:800]}")

    return "\n\n".join(context_parts)


async def chat_with_document(
    document: Any,
    question: str,
    history: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Chat with a document using RAG."""
    if not settings.llm_api_key:
        return {
            "answer": "LLM is not configured. Please add an API key to enable chat.",
            "sources": [],
        }

    context = _get_relevant_context(document, question)

    if not context:
        return {
            "answer": "I couldn't find relevant content in this document to answer your question.",
            "sources": [],
        }

    title = document.title or document.filename

    messages = [
        {
            "role": "system",
            "content": (
                f"You are a research assistant helping analyze the paper '{title}'. "
                "Answer questions based ONLY on the provided context. "
                "If the answer isn't in the context, say so. "
                "Cite page numbers when possible. "
                "Be concise and accurate."
            ),
        }
    ]

    if history:
        for msg in history[-MAX_HISTORY_MESSAGES:]:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", ""),
            })

    messages.append({
        "role": "user",
        "content": f"Context from the paper:\n\n{context}\n\nQuestion: {question}",
    })

    endpoint = f"{settings.llm_base_url.rstrip('/')}/chat/completions"

    payload = {
        "model": settings.llm_model,
        "temperature": 0.3,
        "messages": messages,
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                endpoint,
                headers={
                    "Authorization": f"Bearer {settings.llm_api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()

        data = response.json()
        answer = data["choices"][0]["message"]["content"]

        return {
            "answer": answer,
            "sources": [{"page": 1, "text": context[:200]}],
        }

    except Exception as exc:
        logger.exception("Chat failed: %s", exc)
        return {
            "answer": f"Sorry, I encountered an error: {str(exc)}",
            "sources": [],
        }


async def chat_multi_document(
    documents: list[Any],
    question: str,
    history: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Chat across multiple documents."""
    if not settings.llm_api_key:
        return {
            "answer": "LLM is not configured. Please add an API key to enable chat.",
            "sources": [],
        }

    context_parts = []
    sources = []

    for doc in documents:
        title = doc.title or doc.filename
        context = _get_relevant_context(doc, question)
        if context:
            context_parts.append(f"--- Paper: {title} (ID: {doc.id}) ---\n{context}")
            sources.append({"document_id": doc.id, "title": title})

    if not context_parts:
        return {
            "answer": "I couldn't find relevant content in the selected documents.",
            "sources": [],
        }

    full_context = "\n\n".join(context_parts)

    messages = [
        {
            "role": "system",
            "content": (
                "You are a research assistant helping analyze multiple papers. "
                "Answer questions based ONLY on the provided context. "
                "When comparing papers, cite which paper you're referencing. "
                "Be concise and accurate."
            ),
        }
    ]

    if history:
        for msg in history[-MAX_HISTORY_MESSAGES:]:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", ""),
            })

    messages.append({
        "role": "user",
        "content": f"Context from papers:\n\n{full_context}\n\nQuestion: {question}",
    })

    endpoint = f"{settings.llm_base_url.rstrip('/')}/chat/completions"

    payload = {
        "model": settings.llm_model,
        "temperature": 0.3,
        "messages": messages,
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                endpoint,
                headers={
                    "Authorization": f"Bearer {settings.llm_api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()

        data = response.json()
        answer = data["choices"][0]["message"]["content"]

        return {
            "answer": answer,
            "sources": sources,
        }

    except Exception as exc:
        logger.exception("Multi-doc chat failed: %s", exc)
        return {
            "answer": f"Sorry, I encountered an error: {str(exc)}",
            "sources": [],
        }
