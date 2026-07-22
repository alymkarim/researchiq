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


def clean_pdf_text(value: str) -> str:
    """Clean common PDF extraction problems without removing meaningful numbers."""
    if not value:
        return ""

    value = value.replace("\x00", " ")
    value = value.replace("\u00ad", "")
    value = value.replace("•", " ")
    value = value.replace("▪", " ")
    value = value.replace("■", " ")

    # Join words split across line breaks, such as "nano-\nmaterials".
    value = re.sub(r"(\w)-\s+(\w)", r"\1\2", value)

    # Remove bracketed academic citations, including malformed PDF versions:
    # [1], [1, 2], [1 2], [24-26], [1\n2].
    value = re.sub(
        r"\[\s*\d+(?:\s*[,;–—-]?\s*\d+)*\s*\]",
        " ",
        value,
    )

    # Remove parenthesised numeric citations such as (12) or (12, 13).
    value = re.sub(
        r"\(\s*\d+(?:\s*[,;–—-]\s*\d+)*\s*\)",
        " ",
        value,
    )

    # Repair punctuation and spacing.
    value = re.sub(r"\s+([,.;:!?])", r"\1", value)
    value = re.sub(r"([,.;:!?])(?=[A-Za-z])", r"\1 ", value)
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def clean_output(value: str, maximum_length: int = 900) -> str:
    value = clean_pdf_text(value)

    if not value:
        return "Not clearly stated"

    value = value.strip(" ,;:-")
    return value[:maximum_length].strip()


def make_sentences(text: str) -> list[str]:
    cleaned = clean_pdf_text(text)

    sentences = re.split(
        r"(?<=[.!?])\s+|(?<=;)\s+(?=[A-Z])",
        cleaned,
    )

    ignored_phrases = (
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

    valid_sentences: list[str] = []

    for sentence in sentences:
        sentence = sentence.strip()

        if not 35 <= len(sentence) <= 1800:
            continue

        lowered = sentence.lower()

        if any(phrase in lowered for phrase in ignored_phrases):
            continue

        valid_sentences.append(sentence)

    return valid_sentences


def find_matching_sentences(
    sentences: list[str],
    phrases: list[str],
    limit: int = 2,
) -> list[str]:
    matches: list[str] = []

    for sentence in sentences:
        lowered = sentence.lower()

        if any(phrase in lowered for phrase in phrases):
            cleaned = clean_output(sentence, maximum_length=450)

            if cleaned not in matches:
                matches.append(cleaned)

        if len(matches) >= limit:
            break

    return matches


def split_candidate_points(value: str, limit: int = 4) -> list[str]:
    """
    Convert a long extracted sentence into a few concise points.

    This is especially useful for sentences such as:
    'The material has several properties including high strength,
    good conductivity, large surface area and biocompatibility.'
    """
    value = clean_pdf_text(value)

    if not value:
        return []

    candidate = value

    # Prefer the content after phrases introducing a list.
    list_markers = [
        "including:",
        "including",
        "such as:",
        "such as",
        "advantages include:",
        "advantages include",
        "properties include:",
        "properties including:",
        "characteristics include:",
    ]

    lowered = candidate.lower()

    for marker in list_markers:
        marker_position = lowered.find(marker)

        if marker_position != -1:
            candidate = candidate[marker_position + len(marker):]
            break

    parts = re.split(
        r"\s*[,;]\s*|\s+\band\b\s+",
        candidate,
        flags=re.IGNORECASE,
    )

    points: list[str] = []

    for part in parts:
        part = clean_output(part, maximum_length=220)
        part = part.strip(" .,:;-")

        if len(part) < 12:
            continue

        if part.lower() in {"not clearly stated", "introduction"}:
            continue

        # Avoid returning another enormous paragraph as one bullet.
        if len(part) > 220:
            part = part[:217].rstrip() + "..."

        if part not in points:
            points.append(part[0].upper() + part[1:])

        if len(points) >= limit:
            break

    return points


def format_points(points: list[str], fallback: str) -> str:
    cleaned_points: list[str] = []

    for point in points:
        point = clean_output(point, maximum_length=260)
        point = point.strip(" .,:;-")

        if not point or point == "Not clearly stated":
            continue

        if point not in cleaned_points:
            cleaned_points.append(point)

    if not cleaned_points:
        return fallback

    # Keep the database field as a string while allowing the frontend
    # to display each line as a separate bullet.
    return "\n".join(cleaned_points[:4])


async def analyse_document(text: str, title: str) -> dict[str, str]:
    if (
        settings.llm_api_key
        and settings.llm_base_url
        and settings.llm_model
    ):
        try:
            result = await analyse_with_llm(text, title)
            return normalise_analysis(result)
        except Exception:
            # Fall back to local extraction when the LLM is unavailable.
            pass

    return heuristic_analysis(text)


async def analyse_with_llm(text: str, title: str) -> dict[str, str]:
    prompt = (
        "Analyse the scientific document below and return valid JSON only. "
        "Use exactly these keys: objective, methodology, dataset, findings, "
        "strengths, limitations, keywords. "
        "Every value must be a string. "
        "For strengths and limitations, provide up to four concise statements "
        "separated by newline characters. Do not copy large paragraphs. "
        "Do not treat references, author names, dates, section headings or "
        "generic mentions of future prospects as evidence. "
        "Keywords must be comma-separated. "
        "Do not invent facts. Use 'Not clearly stated' when the document does "
        "not provide enough evidence.\n\n"
        f"Title: {title}\n\n"
        f"Document:\n{clean_pdf_text(text)[:24000]}"
    )

    payload = {
        "model": settings.llm_model,
        "temperature": 0.1,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You extract concise, evidence-based information from "
                    "scientific documents and return JSON only."
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
    content = re.sub(r"^```json\s*", "", content, flags=re.IGNORECASE)
    content = re.sub(r"\s*```$", "", content)

    data = json.loads(content)

    return {
        field: str(data.get(field, "Not clearly stated"))
        for field in FIELDS
    }


def normalise_analysis(data: dict[str, str]) -> dict[str, str]:
    result: dict[str, str] = {}

    for field in FIELDS:
        value = str(data.get(field, "Not clearly stated"))

        if field in {"strengths", "limitations"}:
            points = [
                clean_output(item, maximum_length=260)
                for item in re.split(r"\n+|;\s+", value)
                if item.strip()
            ]

            result[field] = format_points(
                points,
                fallback="Not clearly stated",
            )
        elif field == "keywords":
            result[field] = clean_pdf_text(value)
        else:
            result[field] = clean_output(value)

    return result


def heuristic_analysis(text: str) -> dict[str, str]:
    cleaned = clean_pdf_text(text)
    sentences = make_sentences(cleaned)

    def first_match(
        phrases: list[str],
        fallback: str = "Not clearly stated",
    ) -> str:
        matches = find_matching_sentences(
            sentences,
            phrases,
            limit=1,
        )

        if not matches:
            return fallback

        return clean_output(matches[0], maximum_length=700)

    objective = first_match(
        [
            "the aim of this study",
            "this study aims",
            "the objective of this study",
            "the purpose of this study",
            "this paper aims",
            "this paper presents",
            "this paper provides",
            "this review provides",
            "provides an overview",
            "presents an overview",
            "this chapter introduces",
            "this chapter discusses",
            "this work investigates",
            "we propose",
            "we present",
        ],
        fallback=(
            "The document's central objective was not clearly stated in the "
            "extracted text."
        ),
    )

    methodology = first_match(
        [
            "the proposed method",
            "the methodology",
            "our methodology",
            "we used",
            "we employed",
            "was performed using",
            "was analysed using",
            "experimental procedure",
            "experimental design",
            "machine learning model",
            "deep learning model",
            "the algorithm",
            "the framework",
            "the approach",
        ],
        fallback=(
            "No single experimental methodology was clearly identified. "
            "The document may be a review, overview or collection of methods."
        ),
    )

    dataset = first_match(
        [
            "the dataset consisted",
            "the dataset contains",
            "the dataset included",
            "data were collected",
            "data was collected",
            "participants were",
            "samples were collected",
            "images were obtained",
            "records were obtained",
            "training dataset",
            "training data",
            "test dataset",
            "test data",
            "validation dataset",
            "benchmark dataset",
            "public dataset",
        ],
        fallback=(
            "No specific dataset, participant group or sample was clearly "
            "identified in the extracted text."
        ),
    )

    findings = first_match(
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
            "the findings indicate",
            "the findings suggest",
        ],
        fallback=(
            "No single set of experimental findings was clearly identified. "
            "The document may be an overview or review rather than one study."
        ),
    )

    strength_matches = find_matching_sentences(
        sentences,
        [
            "a strength of this study",
            "strengths of this study",
            "the main strength",
            "an advantage of",
            "advantages include",
            "properties including",
            "properties include",
            "demonstrated robust",
            "achieved high accuracy",
            "achieved strong performance",
            "outperformed",
            "significantly improved",
            "large specific surface area",
            "high sensitivity",
            "high selectivity",
            "biocompatibility",
            "efficient",
            "effective",
        ],
        limit=3,
    )

    strength_points: list[str] = []

    for match in strength_matches:
        extracted = split_candidate_points(match, limit=4)

        if extracted:
            strength_points.extend(extracted)
        else:
            strength_points.append(match)

        if len(strength_points) >= 4:
            break

    strengths = format_points(
        strength_points,
        fallback=(
            "No explicitly stated strengths were identified in the extracted "
            "text."
        ),
    )

    limitation_matches = find_matching_sentences(
        sentences,
        [
            "a limitation of this study",
            "limitations of this study",
            "the main limitation",
            "one limitation",
            "limited by",
            "a drawback",
            "a disadvantage",
            "remains challenging",
            "remains a challenge",
            "major challenge",
            "key challenge",
            "results should be interpreted with caution",
            "further research is needed",
            "future studies should",
            "future work should",
        ],
        limit=4,
    )

    limitation_points: list[str] = []

    for match in limitation_matches:
        # Do not show vague section-introduction text as a limitation.
        lowered = match.lower()

        vague_only = (
            "future prospects and challenges" in lowered
            and not any(
                phrase in lowered
                for phrase in [
                    "limited by",
                    "limitation",
                    "drawback",
                    "disadvantage",
                    "remains challenging",
                    "major challenge",
                    "key challenge",
                ]
            )
        )

        if vague_only:
            continue

        extracted = split_candidate_points(match, limit=3)

        if extracted:
            limitation_points.extend(extracted)
        else:
            limitation_points.append(match)

        if len(limitation_points) >= 4:
            break

    limitations = format_points(
        limitation_points,
        fallback=(
            "No clearly stated limitations were identified in the extracted "
            "text."
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
        "chapter",
        "book",
        "introduction",
        "conclusion",
        "authors",
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