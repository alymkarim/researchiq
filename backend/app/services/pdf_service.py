from pathlib import Path
import re
import pymupdf

def extract_pdf(file_path: str) -> dict:
    pdf = pymupdf.open(file_path)
    pages = [page.get_text("text").strip() for page in pdf]
    pages = [page for page in pages if page]

    full_text = "\n\n".join(pages).strip()
    if not full_text:
        raise ValueError("No readable text was found in this PDF.")

    lines = [line.strip() for line in pages[0].splitlines() if line.strip()]
    title = lines[0][:500] if lines else Path(file_path).stem
    authors = lines[1][:500] if len(lines) > 1 and len(lines[1]) < 300 else None

    abstract = None
    match = re.search(
        r"\babstract\b[:\s-]*(.{100,2500}?)(?=\n\s*(?:1\.?\s+)?(?:introduction|keywords)\b)",
        full_text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if match:
        abstract = " ".join(match.group(1).split())[:2500]

    return {
        "title": title,
        "authors": authors,
        "abstract": abstract,
        "full_text": full_text,
    }
