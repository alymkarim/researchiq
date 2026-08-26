import json
import re
from typing import Any

from openai import OpenAI

from app.config import get_settings


MAX_DOCUMENT_CHARACTERS = 60_000


class LLMAnalysisError(RuntimeError):
    """Raised when the LLM analysis request fails."""


def clean_document_text(text: str) -> str:
    text = text.replace("\x00", " ")

    text = re.sub(
        r"\[\s*\d+(?:\s*,\s*\d+)*\s*\]",
        " ",
        text,
    )

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def truncate_document(text: str) -> str:
    cleaned = clean_document_text(text)

    if len(cleaned) <= MAX_DOCUMENT_CHARACTERS:
        return cleaned

    beginning_size = 35_000
    ending_size = 25_000

    return (
        cleaned[:beginning_size]
        + "\n\n[Middle section omitted because of length]\n\n"
        + cleaned[-ending_size:]
    )


def create_client() -> OpenAI:
    settings = get_settings()

    if not settings.llm_api_key:
        raise LLMAnalysisError(
            "LLM_API_KEY has not been configured."
        )

    client_arguments: dict[str, Any] = {
        "api_key": settings.llm_api_key,
    }

    if settings.llm_base_url:
        client_arguments["base_url"] = settings.llm_base_url

    return OpenAI(**client_arguments)


def extract_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()

    if cleaned.startswith("```"):
        cleaned = re.sub(
            r"^```(?:json)?\s*",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise LLMAnalysisError(
            "The LLM returned invalid JSON."
        ) from exc

    if not isinstance(parsed, dict):
        raise LLMAnalysisError(
            "The LLM response was not a JSON object."
        )

    return parsed


def normalise_list(value: Any, maximum: int = 5) -> list[str]:
    if not isinstance(value, list):
        return []

    results: list[str] = []

    for item in value:
        text = str(item).strip()

        if text and text not in results:
            results.append(text)

    return results[:maximum]


def normalise_text(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip()


def analyse_with_llm(
    *,
    title: str,
    text: str,
) -> dict[str, Any]:
    settings = get_settings()
    client = create_client()

    document_text = truncate_document(text)

    prompt = f"""
You are analysing a scientific research paper.

Return only valid JSON. Do not use Markdown or code fences.

Use evidence from the paper only. Do not invent missing information.
When information is unavailable, use an empty string or empty list.

Required JSON structure:

{{
  "summary": "A concise executive summary of the paper.",
  "objective": "The main research question or objective.",
  "methodology": "The research design, methods, models or experiments.",
  "dataset": "The dataset, sample, participants or experimental material.",
  "findings": "The main findings and results.",
  "strengths": [
    "Concise evidence-based strength"
  ],
  "limitations": [
    "Concise evidence-based limitation"
  ],
  "keywords": [
    "keyword"
  ]
}}

Rules:

1. Keep the summary under 180 words.
2. Keep objective, methodology, dataset and findings under 120 words each.
3. Return at most four strengths.
4. Return at most four limitations.
5. Return between five and ten keywords when possible.
6. Do not treat general future work as a limitation unless the paper
   explicitly identifies a current limitation.
7. Do not copy references, citation numbers, page headers or footers.
8. Do not make claims that are unsupported by the supplied paper.

Paper title:
{title}

Paper text:
{document_text}
""".strip()

    try:
        response = client.responses.create(
            model=settings.llm_model,
            instructions=(
                "You are a careful scientific literature analyst. "
                "Return accurate structured JSON based only on supplied text."
            ),
            input=prompt,
        )
    except Exception as exc:
        raise LLMAnalysisError(
            f"LLM analysis failed: {exc}"
        ) from exc

    output_text = response.output_text

    if not output_text:
        raise LLMAnalysisError(
            "The LLM returned an empty response."
        )

    result = extract_json(output_text)

    return {
        "summary": normalise_text(result.get("summary")),
        "objective": normalise_text(result.get("objective")),
        "methodology": normalise_text(result.get("methodology")),
        "dataset": normalise_text(result.get("dataset")),
        "findings": normalise_text(result.get("findings")),
        "strengths": normalise_list(
            result.get("strengths"),
            maximum=4,
        ),
        "limitations": normalise_list(
            result.get("limitations"),
            maximum=4,
        ),
        "keywords": normalise_list(
            result.get("keywords"),
            maximum=10,
        ),
    }