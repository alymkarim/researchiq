import re


def clean_text(value: str | None) -> str:
    """Clean common PDF extraction artefacts."""
    if not value:
        return ""

    value = value.replace("\x00", " ")
    value = value.replace("\u00ad", "")
    value = value.replace("•", " ")
    value = value.replace("▪", " ")
    value = value.replace("■", " ")

    value = re.sub(r"(\w)-\s+(\w)", r"\1\2", value)
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def clean_for_analysis(value: str | None) -> str:
    """Aggressive cleaning for LLM/heuristic analysis input."""
    cleaned = clean_text(value)

    cleaned = re.sub(
        r"\[\s*\d+(?:\s*[,;\u2013\u2014-]?\s*\d+)*\s*\]", " ", cleaned
    )
    cleaned = re.sub(
        r"\(\s*\d+(?:\s*[,;\u2013\u2014-]\s*\d+)*\s*\)", " ", cleaned
    )
    cleaned = re.sub(r"\s+([,.;:!?])", r"\1", cleaned)
    cleaned = re.sub(r"([,.;:!?])(?=[A-Za-z])", r"\1 ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)

    return cleaned.strip()