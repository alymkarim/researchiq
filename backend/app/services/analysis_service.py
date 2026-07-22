import json
import re
from collections import Counter
import httpx
from ..config import settings

FIELDS = ["objective", "methodology", "dataset", "findings", "limitations", "keywords"]

async def analyse_document(text: str, title: str) -> dict[str, str]:
    if settings.llm_api_key and settings.llm_base_url and settings.llm_model:
        try:
            return await analyse_with_llm(text, title)
        except Exception:
            pass
    return heuristic_analysis(text)

async def analyse_with_llm(text: str, title: str) -> dict[str, str]:
    prompt = (
        "Analyse this scientific paper and return valid JSON only with these keys: "
        "objective, methodology, dataset, findings, limitations, keywords. "
        "Each value must be a string. Keywords must be comma-separated. "
        "Do not invent missing facts.\n\n"
        f"Title: {title}\n\nPaper:\n{text[:24000]}"
    )

    payload = {
        "model": settings.llm_model,
        "temperature": 0.1,
        "messages": [
            {"role": "system", "content": "You extract structured evidence from scientific papers."},
            {"role": "user", "content": prompt},
        ],
    }

    async with httpx.AsyncClient(timeout=90) as client:
        response = await client.post(
            f"{settings.llm_base_url.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {settings.llm_api_key}"},
            json=payload,
        )
        response.raise_for_status()

    content = response.json()["choices"][0]["message"]["content"].strip()
    content = re.sub(r"^```json\s*", "", content)
    content = re.sub(r"\s*```$", "", content)
    data = json.loads(content)

    return {field: str(data.get(field, "Not clearly stated")) for field in FIELDS}

def heuristic_analysis(text: str) -> dict[str, str]:
    cleaned = " ".join(text.split())
    sentences = re.split(r"(?<=[.!?])\s+", cleaned)

    def first_matching(terms: list[str]) -> str:
        for sentence in sentences:
            if any(term in sentence.lower() for term in terms):
                return sentence[:700]
        return "Not clearly stated"

    stopwords = {
        "the", "and", "for", "that", "with", "this", "from", "were", "was",
        "are", "have", "has", "using", "into", "their", "these", "which",
        "our", "they", "been", "can", "than", "also", "between", "study",
    }
    words = re.findall(r"\b[a-zA-Z][a-zA-Z-]{3,}\b", cleaned.lower())
    counts = Counter(word for word in words if word not in stopwords)
    keywords = ", ".join(word for word, _ in counts.most_common(8))

    return {
        "objective": first_matching(["aim", "objective", "purpose", "we propose", "this study"]),
        "methodology": first_matching(["method", "approach", "model", "algorithm", "experiment"]),
        "dataset": first_matching(["dataset", "sample", "participants", "images", "records"]),
        "findings": first_matching(["result", "achieved", "found", "performance", "accuracy"]),
        "limitations": first_matching(["limitation", "however", "future work", "constraint"]),
        "keywords": keywords,
    }
