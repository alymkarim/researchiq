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
        if len(sentence.strip()) >= 40
    ]

    def sentence_matches(sentence: str, phrases: list[str]) -> bool:
        lowered = sentence.lower()
        return any(phrase in lowered for phrase in phrases)

    def first_matching(
        phrases: list[str],
        fallback: str = "Not clearly stated",
    ) -> str:
        for sentence in sentences:
            if sentence_matches(sentence, phrases):
                return sentence[:700]

        return fallback

    objective = first_matching(
        [
            "the aim of this study",
            "this study aims",
            "the objective of this study",
            "the purpose of this study",
            "we propose",
            "we present",
            "this paper proposes",
            "this paper presents",
            "this work investigates",
        ]
    )

    methodology = first_matching(
        [
            "the proposed method",
            "our methodology",
            "the methodology",
            "we used",
            "we employed",
            "was performed using",
            "was analysed using",
            "experimental procedure",
            "machine learning model",
            "deep learning model",
            "algorithm was",
        ]
    )

    dataset = first_matching(
        [
            "the dataset consisted",
            "the dataset contains",
            "the dataset included",
            "data were collected",
            "data was collected",
            "participants were",
            "samples were",
            "images were obtained",
            "records were obtained",
            "training dataset",
            "test dataset",
            "validation dataset",
        ],
        fallback=(
            "No clearly described dataset, sample or participant group "
            "was identified."
        ),
    )

    findings = first_matching(
        [
            "the results show",
            "the results showed",
            "results demonstrate",
            "results demonstrated",
            "we found that",
            "the study found",
            "achieved an accuracy",
            "achieved a performance",
            "outperformed",
            "significantly improved",
        ]
    )

    strengths = first_matching(
        [
            "a strength of this study",
            "strengths of this study",
            "the main strength",
            "an advantage of this method",
            "an advantage of the proposed",
            "our method outperformed",
            "the proposed method outperformed",
            "demonstrated robust performance",
            "achieved high accuracy",
            "achieved strong performance",
            "provides a comprehensive",
            "offers a practical",
        ],
        fallback=(
            "No explicitly stated strengths were identified. "
            "Review the methodology and results to infer potential strengths."
        ),
    )

    limitations = first_matching(
        [
            "a limitation of this study",
            "limitations of this study",
            "the main limitation",
            "one limitation",
            "study limitations",
            "limited by",
            "results should be interpreted with caution",
            "further research is needed",
            "future studies should",
            "future work should",
        ],
        fallback=(
            "No clearly stated limitations were identified. "
            "Review the discussion and conclusion for possible constraints."
        ),
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
    }

    words = re.findall(
        r"\b[a-zA-Z][a-zA-Z-]{3,}\b",
        cleaned.lower(),
    )

    counts = Counter(
        word
        for word in words
        if word not in stopwords
    )

    keywords = ", ".join(
        word
        for word, _ in counts.most_common(8)
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