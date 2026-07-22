import json
import re
from collections import Counter

import httpx

from ..config import settings


FIELDS = [
    "objective",
    "methodology",
    "dataset",
    "findings",
    "strengths",
    "limitations",
    "keywords",
]


async def analyse_document(text: str, title: str) -> dict[str, str]:
    if (
        settings.llm_api_key
        and settings.llm_base_url
        and settings.llm_model
    ):
        try:
            return await analyse_with_llm(text, title)
        except Exception:
            pass

    return heuristic_analysis(text)


async def analyse_with_llm(text: str, title: str) -> dict[str, str]:
    prompt = (
        "Analyse this scientific paper and return valid JSON only with these keys: "
        "objective, methodology, dataset, findings, strengths, limitations, keywords. "
        "Each value must be a string. Keywords must be comma-separated. "
        "Strengths and limitations must be evidence-based and specific to the paper. "
        "Do not invent missing facts. If something is not clearly stated, return "
        "'Not clearly stated'.\n\n"
        f"Title: {title}\n\n"
        f"Paper:\n{text[:24000]}"
    )

    payload = {
        "model": settings.llm_model,
        "temperature": 0.1,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You extract accurate, structured evidence from scientific papers. "
                    "Return JSON only."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    }

    async with httpx.AsyncClient(timeout=90) as client:
        response = await client.post(
            f"{settings.llm_base_url.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.llm_api_key}",
            },
            json=payload,
        )
        response.raise_for_status()

    content = response.json()["choices"][0]["message"]["content"].strip()
    content = re.sub(r"^```json\s*", "", content)
    content = re.sub(r"\s*```$", "", content)

    data = json.loads(content)

    return {
        field: str(data.get(field, "Not clearly stated"))
        for field in FIELDS
    }


def heuristic_analysis(text: str) -> dict[str, str]:
    cleaned = " ".join(text.replace("\x00", " ").split())

    sentences = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", cleaned)
        if 35 <= len(sentence.strip()) <= 1200
    ]

    def find_sentences(
        phrases: list[str],
        limit: int = 2,
    ) -> str | None:
        matches: list[str] = []

        for sentence in sentences:
            lowered = sentence.lower()

            if any(phrase in lowered for phrase in phrases):
                matches.append(sentence)

            if len(matches) >= limit:
                break

        if not matches:
            return None

        return " ".join(matches)[:1000]

    def first_substantial_sentences(
        start: int = 0,
        count: int = 2,
    ) -> str:
        selected: list[str] = []

        for sentence in sentences[start:]:
            lowered = sentence.lower()

            if any(
                unwanted in lowered
                for unwanted in [
                    "copyright",
                    "isbn",
                    "all rights reserved",
                    "table of contents",
                    "published by",
                    "http://",
                    "https://",
                ]
            ):
                continue

            selected.append(sentence)

            if len(selected) >= count:
                break

        return " ".join(selected)[:1000] or "Not clearly stated"

    objective = find_sentences(
        [
            "aim",
            "objective",
            "purpose",
            "focuses on",
            "provides an overview",
            "presents an overview",
            "introduces",
            "explores",
            "examines",
            "investigates",
            "discusses",
            "this paper",
            "this chapter",
            "this book",
            "this work",
            "we propose",
            "we present",
        ]
    )

    if not objective:
        objective = first_substantial_sentences(0, 2)

    methodology = find_sentences(
        [
            "method",
            "methodology",
            "approach",
            "algorithm",
            "model",
            "framework",
            "technique",
            "procedure",
            "experiment",
            "implemented",
            "trained",
            "evaluated",
            "classification",
            "regression",
            "neural network",
            "machine learning",
            "deep learning",
        ]
    )

    if not methodology:
        methodology = (
            "No single experimental methodology was clearly identified. "
            "The document appears to discuss multiple machine-learning "
            "methods, algorithms or applications."
        )

    dataset = find_sentences(
        [
            "dataset",
            "data set",
            "database",
            "data were",
            "data was",
            "samples",
            "participants",
            "images",
            "records",
            "training data",
            "test data",
            "validation data",
            "benchmark",
            "corpus",
        ]
    )

    if not dataset:
        dataset = (
            "No specific dataset was clearly identified in the extracted text."
        )

    findings = find_sentences(
        [
            "results",
            "findings",
            "showed",
            "demonstrated",
            "achieved",
            "accuracy",
            "performance",
            "outperformed",
            "improved",
            "concluded",
            "conclusion",
            "suggests that",
            "indicates that",
        ]
    )

    if not findings:
        findings = (
            "No single set of experimental findings was clearly identified. "
            "The document may be an overview, textbook chapter or collection "
            "rather than one experimental study."
        )

    strengths = find_sentences(
        [
            "strength",
            "advantage",
            "benefit",
            "effective",
            "robust",
            "high accuracy",
            "high performance",
            "outperformed",
            "improved",
            "efficient",
            "comprehensive",
            "practical",
            "novel",
        ]
    )

    if not strengths:
        strengths = (
            "The document provides broad coverage of machine-learning "
            "algorithms and applications, although explicit strengths were "
            "not stated in a dedicated section."
        )

    limitations = find_sentences(
        [
            "limitation",
            "limited by",
            "drawback",
            "disadvantage",
            "challenge",
            "constraint",
            "future work",
            "future research",
            "further research",
            "should be interpreted with caution",
            "remains difficult",
            "remains challenging",
        ]
    )

    if not limitations:
        limitations = (
            "No explicit limitations section was identified. Because the "
            "document covers a broad topic, the extracted text may not describe "
            "the constraints of one specific experiment."
        )

    stopwords = {
        "the",
        "and",
        "for",
        "that",
        "with",
        "this",
        "from",
        "were",
        "was",
        "are",
        "have",
        "has",
        "using",
        "into",
        "their",
        "these",
        "which",
        "our",
        "they",
        "been",
        "can",
        "than",
        "also",
        "between",
        "study",
        "paper",
        "results",
        "method",
        "methods",
        "research",
        "based",
        "chapter",
        "book",
    }

    words = re.findall(
        r"\b[a-zA-Z][a-zA-Z-]{3,}\b",
        cleaned.lower(),
    )

    counts = Counter(
        word for word in words
        if word not in stopwords
    )

    keywords = ", ".join(
        word for word, _ in counts.most_common(8)
    )

    return {
        "objective": objective,
        "methodology": methodology,
        "dataset": dataset,
        "findings": findings,
        "strengths": strengths,
        "limitations": limitations,
        "keywords": keywords,
    }