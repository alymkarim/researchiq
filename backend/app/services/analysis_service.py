import json
import logging
import re
import time
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

MAX_LLM_CHARACTERS = 8_000


def prepare_llm_document(text: str) -> str:
    cleaned = clean_pdf_text(text)

    if len(cleaned) <= MAX_LLM_CHARACTERS:
        return cleaned

    # Preserve the opening and ending because abstracts/methods usually occur
    # near the beginning while limitations/conclusions often occur near the end.
    beginning = cleaned[:5_000]
    ending = cleaned[-3_000:]

    return (
        beginning
        + "\n\n[Middle section omitted because the document was long.]\n\n"
        + ending
    )


def clean_output(value: Any, maximum_length: int = 1_200) -> str:
    if value is None:
        return "Not clearly stated"

    if isinstance(value, dict):
        parts = []
        for k, v in value.items():
            parts.append(f"{k}: {clean_output(v, 200)}")
        value = "; ".join(parts)
    elif isinstance(value, list):
        value = ", ".join(str(item) for item in value)

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

    # Recursively parse JSON strings within the object
    for key, value in parsed.items():
        if isinstance(value, str):
            # Try to parse JSON strings
            try:
                parsed[key] = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                pass

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

    prompt = f"""You are analyzing a scientific research paper. Your task is to extract key information and return it as JSON.

IMPORTANT: You MUST return a JSON object with EXACTLY these fields:
- "summary": A 2-3 sentence summary of the paper
- "objective": The main research goal or question
- "methodology": The methods/approach used
- "dataset": The data or samples used
- "findings": The main results
- "strengths": Array of 2-4 strengths
- "limitations": Array of 2-4 limitations  
- "keywords": Array of 5-10 keywords

DO NOT return raw data from the paper. Return ANALYSIS of the paper.

Paper title: {title}

Paper text:
{document}

Return ONLY the JSON object, nothing else."""

    endpoint = f"{settings.llm_base_url.rstrip('/')}/chat/completions"

    payload = {
        "model": settings.llm_model,
        "temperature": 0.1,
        "messages": [
            {
                "role": "system",
                "content": "You are a scientific paper analyst. Return JSON with summary, objective, methodology, dataset, findings, strengths, limitations, and keywords.",
            },
            {"role": "user", "content": prompt},
        ],
    }

    # Only add response_format for OpenAI-compatible APIs (not Ollama)
    if "ollama" not in settings.llm_base_url.lower():
        payload["response_format"] = {"type": "json_object"}

    response = None
    async with httpx.AsyncClient(timeout=120) as client:
        for attempt in range(3):
            response = await client.post(
                endpoint,
                headers={
                    "Authorization": f"Bearer {settings.llm_api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

            # Rate limited - wait and retry
            if response.status_code == 429:
                wait_time = 5 * (attempt + 1)
                print(f"Rate limited, waiting {wait_time}s before retry...")
                time.sleep(wait_time)
                continue

            # Payload too large - reduce text size
            if response.status_code == 413:
                print("Payload too large, reducing text size...")
                document = document[:4000]
                payload["messages"][1]["content"] = f"Paper text:\n\n{document}\n\nAnalyze this paper and return JSON with summary, objective, methodology, dataset, findings, strengths, limitations, and keywords."
                continue

            # Some providers do not support response_format.
            if response.status_code in {400, 422} and "response_format" in payload:
                payload.pop("response_format", None)
                response = await client.post(
                    endpoint,
                    headers={
                        "Authorization": f"Bearer {settings.llm_api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )

            break

    if response is None:
        raise ValueError("No response received from LLM provider")
    
    response.raise_for_status()

    response_data = response.json()
    content = response_data["choices"][0]["message"]["content"]
    
    # Debug logging
    print(f"LLM response content: {content[:500]}")
    
    parsed = extract_json_object(content)
    
    # Debug logging
    print(f"Parsed JSON: {parsed}")
    
    # Check if the response has the expected fields
    expected_fields = ["summary", "objective", "methodology", "dataset", "findings"]
    has_expected_fields = any(field in parsed for field in expected_fields)
    
    if not has_expected_fields:
        print("LLM did not return expected fields, using heuristic fallback")
        fallback = heuristic_analysis(text)
        fallback["analysis_mode"] = "heuristic"
        return fallback

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
