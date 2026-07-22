def test_rejects_non_pdf(client):
    response = client.post(
        "/api/documents/upload",
        files=[
            (
                "files",
                (
                    "notes.txt",
                    b"This is not a PDF.",
                    "text/plain",
                ),
            )
        ],
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF files are supported."


def test_rejects_empty_pdf(client):
    response = client.post(
        "/api/documents/upload",
        files=[
            (
                "files",
                (
                    "empty.pdf",
                    b"",
                    "application/pdf",
                ),
            )
        ],
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "The uploaded PDF is empty."