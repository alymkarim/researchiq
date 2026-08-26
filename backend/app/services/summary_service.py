import logging
from typing import Any

import httpx

from ..config import settings
from ..utils.text import clean_for_analysis

logger = logging.getLogger(__name__)

SUMMARY_LEVELS = {
    "quick": {
        "max_chars": 5000,
        "prompt": "Provide a very brief 2-3 sentence summary of this paper.",
        "max_tokens": 200,
    },
    "standard": {
        "max_chars": 20000,
        "prompt": "Provide a structured analysis with summary, objective, methodology, findings, strengths, and limitations.",
        "max_tokens": 1500,
    },
    "deep": {
        "max_chars": 50000,
        "prompt": "Provide an in-depth analysis including detailed methodology review, statistical analysis discussion, literature context, and critical evaluation.",
        "max_tokens": 3000,
    },
}


async def analyse_with_level(
    text: str,
    title: str,
    level: str = "standard",
) -> dict[str, Any]:
    """Analyse a document at the specified depth level."""
    if level not in SUMMARY_LEVELS:
        level = "standard"

    config = SUMMARY_LEVELS[level]

    if not settings.llm_api_key:
        return {
            "level": level,
            "analysis": None,
            "error": "LLM not configured.",
        }

    cleaned = clean_for_analysis(text)
    if len(cleaned) > config["max_chars"]:
        beginning = cleaned[: config["max_chars"] * 2 // 3]
        ending = cleaned[-config["max_chars"] // 3 :]
        cleaned = beginning + "\n\n[Middle section omitted.]\n\n" + ending

    if level == "quick":
        prompt = f"""{config['prompt']}

Paper title: {title}

Paper text:
{cleaned}

Return a brief 2-3 sentence summary only."""

    elif level == "deep":
        prompt = f"""{config['prompt']}

Paper title: {title}

Paper text:
{cleaned}

Return JSON with these fields:
{{
  "summary": "Detailed executive summary (200-300 words)",
  "objective": "Research objective with context",
  "methodology": "Detailed methodology review including strengths and weaknesses of the approach",
  "dataset": "Dataset description with sample size, characteristics, and limitations",
  "findings": "Detailed findings with key statistics and significance",
  "strengths": ["List of evidence-based strengths"],
  "limitations": ["List of evidence-based limitations"],
  "future_work": "Suggested future research directions",
  "literature_context": "How this work fits in the broader literature",
  "critical_evaluation": "Critical assessment of the work's contribution",
  "keywords": ["keyword1", "keyword2"]
}}"""

    else:
        prompt = f"""{config['prompt']}

Paper title: {title}

Paper text:
{cleaned}

Return JSON with these fields:
{{
  "summary": "Concise executive summary",
  "objective": "Main research objective",
  "methodology": "Research methods used",
  "dataset": "Dataset or sample description",
  "findings": "Main results",
  "strengths": ["strength1", "strength2"],
  "limitations": ["limitation1", "limitation2"],
  "keywords": ["keyword1", "keyword2"]
}}"""

    endpoint = f"{settings.llm_base_url.rstrip('/')}/chat/completions"

    payload = {
        "model": settings.llm_model,
        "temperature": 0.1,
        "max_tokens": config["max_tokens"],
        "messages": [
            {
                "role": "system",
                "content": "You are a scientific literature analyst. Return concise, evidence-based analysis.",
            },
            {"role": "user", "content": prompt},
        ],
    }

    if level != "quick":
        payload["response_format"] = {"type": "json_object"}

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                endpoint,
                headers={
                    "Authorization": f"Bearer {settings.llm_api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

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

            response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        if level == "quick":
            return {
                "level": level,
                "analysis": {"summary": content},
            }

        import json
        import re

        content = content.strip()
        content = re.sub(r"^```(?:json)?\s*", "", content, flags=re.IGNORECASE)
        content = re.sub(r"\s*```$", "", content)

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1 and end > start:
                parsed = json.loads(content[start : end + 1])
            else:
                parsed = {"summary": content}

        return {
            "level": level,
            "analysis": parsed,
        }

    except Exception as exc:
        logger.exception("Analysis at level %s failed: %s", level, exc)
        return {
            "level": level,
            "analysis": None,
            "error": str(exc),
        }
