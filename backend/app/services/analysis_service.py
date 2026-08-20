import json
import logging
import re
from collections import Counter
from typing import Any

import httpx

from ..config import settings
from ..utils.text import clean_for_analysis as clean_pdf_text


logger = logging.getLogger(__name__)

ANALYSIS_FIELDS = [
    "summary",
    "objective",
    "methodology",
    "dataset",
    "findings",
    "strengths",
    "limitations",
    "keywords",
]

MAX_LLM_CHARACTERS = 50_000


def prepare_llm_document(text: str) -> str:
    cleaned = clean_pdf_text(text)

    if len(cleaned) <= MAX_LLM_CHARACTERS:
        return cleaned

    # Preserve the opening and ending because abstracts/methods usually occur
    # near the beginning while limitations/conclusions often occur near the end.
    beginning = cleaned[:32_000]
    ending = cleaned[-18_000:]

    return (
        beginning
        + "\n\n[Middle section omitted because the document was long.]\n\n"
        + ending
    )


def clean_output(value: Any, maximum_length: int = 1_200) -> str:
    if value is None:
        return "Not clearly stated"

    cleaned = clean_pdf_text(str(value)).strip(" ,;:-")

    if not cleaned:
        return "Not clearly stated"

    if len(cleaned) > maximum_length:
        return cleaned[: maximum_length - 3].rstrip() + "..."

    return cleaned


def normalise_points(value: Any, maximum: int = 4) -> str:
    if isinstance(value, list):
        candidates = [str(item) for item in value]
    else:
        candidates = re.split(r"\n+|;\s+|\s*•\s*", str(value or ""))

    points: list[str] = []

    for item in candidates:
        cleaned = clean_output(item, maximum_length=280)
        cleaned = re.sub(r"^\s*[-*•\d.)]+\s*", "", cleaned).strip()

        if cleaned == "Not clearly stated":
            continue

        if cleaned and cleaned not in points:
            points.append(cleaned)

        if len(points) >= maximum:
            break

    return "\n".join(points) if points else "Not clearly stated"


def normalise_keywords(value: Any) -> str:
    if isinstance(value, list):
        candidates = [str(item) for item in value]
    else:
        candidates = re.split(r",|\n|;", str(value or ""))

    keywords: list[str] = []

    for item in candidates:
        cleaned = clean_pdf_text(item).strip(" ,.;:-").lower()

        if cleaned and cleaned not in keywords:
            keywords.append(cleaned)

        if len(keywords) >= 10:
            break

    return ", ".join(keywords) if keywords else "Not clearly stated"


def extract_json_object(content: str) -> dict[str, Any]:
    content = content.strip()
    content = re.sub(r"^```(?:json)?\s*", "", content, flags=re.IGNORECASE)
    content = re.sub(r"\s*```$", "", content)

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")

        if start == -1 or end == -1 or end <= start:
            raise ValueError("The LLM response did not contain a JSON object.")

        parsed = json.loads(content[start : end + 1])

    if not isinstance(parsed, dict):
        raise ValueError("The LLM response was not a JSON object.")

    return parsed


def normalise_analysis(data: dict[str, Any]) -> dict[str, str]:
    return {
        "summary": clean_output(data.get("summary"), maximum_length=1_400),
        "objective": clean_output(data.get("objective"), maximum_length=1_000),
        "methodology": clean_output(data.get("methodology"), maximum_length=1_200),
        "dataset": clean_output(data.get("dataset"), maximum_length=1_000),
        "findings": clean_output(data.get("findings"), maximum_length=1_200),
        "strengths": normalise_points(data.get("strengths"), maximum=4),
        "limitations": normalise_points(data.get("limitations"), maximum=4),
        "keywords": normalise_keywords(data.get("keywords")),
    }


async def analyse_document(text: str, title: str) -> dict[str, str]:
    """
    Use the configured LLM when credentials exist.

    If the request fails, ResearchIQ continues working by falling back to the
    local heuristic analyser.
    """
    if settings.llm_api_key and settings.llm_model:
        try:
            result = await analyse_with_llm(text=text, title=title)
            result["analysis_mode"] = "llm"
            return result
        except Exception as exc:
            logger.exception("LLM analysis failed; using heuristic fallback: %s", exc)

    fallback = heuristic_analysis(text)
    fallback["analysis_mode"] = "heuristic"
    return fallback


async def analyse_with_llm(text: str, title: str) -> dict[str, str]:
    document = prepare_llm_document(text)

    prompt = f"""
Analyse the scientific paper below.

Return valid JSON only, with exactly this structure:

{{
  "summary": "Concise executive summary",
  "objective": "Main research objective or question",
  "methodology": "Research design, methods, models, experiments or procedures",
  "dataset": "Dataset, samples, participants or experimental material",
  "findings": "Main results and conclusions",
  "strengths": [
    "Evidence-based strength"
  ],
  "limitations": [
    "Evidence-based limitation"
  ],
  "keywords": [
    "keyword"
  ]
}}

Rules:
1. Use only evidence contained in the supplied paper.
2. Do not invent details.
3. Use "Not clearly stated" when evidence is missing.
4. Keep the summary below 180 words.
5. Keep objective, methodology, dataset and findings concise.
6. Return at most four strengths and four limitations.
7. Do not treat vague future-work statements as current limitations.
8. Do not copy references, page headers, footers or citation markers.
9. Return five to ten useful keywords where possible.
10. Return JSON only, without Markdown fences.

Paper title:
{title}

Paper text:
{document}
""".strip()

    endpoint = f"{settings.llm_base_url.rstrip('/')}/chat/completions"

    payload = {
        "model": settings.llm_model,
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a careful scientific literature analyst. "
                    "Return concise, evidence-based structured JSON."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    }

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {settings.llm_api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )

        # Some OpenAI-compatible providers do not support response_format.
        if response.status_code in {400, 422}:
            payload.pop("response_format", None)
            response = await client.post(
                endpoint,
                headers={
                    "Authorization": f"Bearer {settings.llm_api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

        response.raise_for_status()

    response_data = response.json()
    content = response_data["choices"][0]["message"]["content"]
    parsed = extract_json_object(content)

    return normalise_analysis(parsed)


def make_sentences(text: str) -> list[str]:
    cleaned = clean_pdf_text(text)
    sentences = re.split(r"(?<=[.!?])\s+|(?<=;)\s+(?=[A-Z])", cleaned)

    ignored = (
        "all rights reserved",
        "copyright",
        "isbn",
        "table of contents",
        "downloaded from",
        "available online",
        "published by",
        "http://",
        "https://",
    )

    return [
        sentence.strip()
        for sentence in sentences
        if 35 <= len(sentence.strip()) <= 1_800
        and not any(term in sentence.lower() for term in ignored)
    ]


def find_first(sentences: list[str], phrases: list[str], fallback: str) -> str:
    for sentence in sentences:
        lowered = sentence.lower()

        if any(phrase in lowered for phrase in phrases):
            return clean_output(sentence, maximum_length=800)

    return fallback


def collect_points(
    sentences: list[str],
    phrases: list[str],
    fallback: str,
) -> str:
    matches: list[str] = []

    for sentence in sentences:
        lowered = sentence.lower()

        if any(phrase in lowered for phrase in phrases):
            cleaned = clean_output(sentence, maximum_length=280)

            if cleaned not in matches:
                matches.append(cleaned)

        if len(matches) >= 4:
            break

    return "\n".join(matches) if matches else fallback


def heuristic_analysis(text: str) -> dict[str, str]:
    cleaned = clean_pdf_text(text)
    sentences = make_sentences(cleaned)

    objective = find_first(
        sentences,
        [
            "the aim of this study",
            "this study aims",
            "the objective of this study",
            "the purpose of this study",
            "this paper aims",
            "this work investigates",
            "we propose",
            "we present",
        ],
        "The document's central objective was not clearly stated.",
    )

    methodology = find_first(
        sentences,
        [
            "the proposed method",
            "the methodology",
            "we used",
            "we employed",
            "experimental procedure",
            "experimental design",
            "machine learning model",
            "deep learning model",
            "the framework",
            "the approach",
        ],
        "No single methodology was clearly identified.",
    )

    dataset = find_first(
        sentences,
        [
            "the dataset consisted",
            "the dataset contains",
            "the dataset included",
            "data were collected",
            "participants were",
            "samples were collected",
            "training dataset",
            "test dataset",
            "benchmark dataset",
            "public dataset",
        ],
        "No specific dataset, sample or participant group was clearly identified.",
    )

    findings = find_first(
        sentences,
        [
            "the results show",
            "the results showed",
            "results demonstrate",
            "we found that",
            "the study found",
            "achieved an accuracy",
            "outperformed",
            "the findings indicate",
            "the findings suggest",
        ],
        "No single set of findings was clearly identified.",
    )

    strengths = collect_points(
        sentences,
        [
            "a strength of this study",
            "strengths of this study",
            "the main strength",
            "an advantage of",
            "advantages include",
            "achieved high accuracy",
            "achieved strong performance",
            "outperformed",
            "significantly improved",
            "high sensitivity",
            "high selectivity",
        ],
        "No explicitly stated strengths were identified.",
    )

    limitations = collect_points(
        sentences,
        [
            "a limitation of this study",
            "limitations of this study",
            "the main limitation",
            "one limitation",
            "limited by",
            "a drawback",
            "a disadvantage",
            "results should be interpreted with caution",
        ],
        "No clearly stated limitations were identified.",
    )

    stopwords = {
        "the", "and", "for", "that", "with", "this", "from", "were", "was",
        "are", "have", "has", "using", "into", "their", "these", "which",
        "our", "they", "been", "can", "than", "also", "between", "study",
        "paper", "results", "method", "methods", "research", "based",
        "chapter", "book", "introduction", "conclusion", "authors",
    }

    words = re.findall(r"\b[a-zA-Z][a-zA-Z-]{3,}\b", cleaned.lower())
    counts = Counter(word for word in words if word not in stopwords)
    keywords = ", ".join(word for word, _ in counts.most_common(8))

    summary_parts = [
        value
        for value in [objective, methodology, findings]
        if "not clearly" not in value.lower()
    ]
    summary = " ".join(summary_parts)[:1_400] or "Not clearly stated"

    return {
        "summary": summary,
        "objective": objective,
        "methodology": methodology,
        "dataset": dataset,
        "findings": findings,
        "strengths": strengths,
        "limitations": limitations,
        "keywords": keywords or "Not clearly stated",
    }
