def to_bibtex(doc) -> str:
    year = doc.created_at.year if doc.created_at else "nd"
    if doc.authors:
        first_author = doc.authors.split(",")[0].split()[-1].lower()
    else:
        first_author = doc.filename.split(".")[0].lower()[:20]
    key = f"{first_author}{year}"
    authors = doc.authors or "Unknown"
    title = doc.title or doc.filename
    return f"""@article{{{key},
  title={{{title}}},
  author={{{authors}}},
  year={{{year}}},
  note={{Accessed via ResearchIQ}}
}}"""


def to_apa(doc) -> str:
    authors = doc.authors or "Unknown"
    year = doc.created_at.year if doc.created_at else "n.d."
    title = doc.title or doc.filename
    return f"{authors} ({year}). {title}. ResearchIQ."


def to_mla(doc) -> str:
    authors = doc.authors or "Unknown"
    title = doc.title or doc.filename
    return f'{authors}. "{title}." ResearchIQ, {doc.created_at.year if doc.created_at else "n.d."}.'
