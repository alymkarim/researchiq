import json
from types import SimpleNamespace

from app.services.search_service import search_documents


def test_search_returns_matching_text_and_page():
    document = SimpleNamespace(
        id=1,
        title="Machine Learning Study",
        filename="machine-learning.pdf",
        full_text="",
        pages_json=json.dumps(
            [
                {
                    "page": 1,
                    "text": "This page discusses the introduction.",
                },
                {
                    "page": 4,
                    "text": (
                        "The machine learning dataset contained "
                        "five thousand labelled images."
                    ),
                },
            ]
        ),
    )

    results = search_documents(
        [document],
        "Which dataset was used?",
        limit=5,
    )

    assert len(results) >= 1
    assert results[0]["document_id"] == 1
    assert results[0]["page"] == 4
    assert "dataset" in results[0]["text"].lower()


def test_search_returns_empty_list_without_documents():
    results = search_documents(
        [],
        "machine learning",
        limit=5,
    )

    assert results == []