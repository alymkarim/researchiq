import pytest


def test_register_success(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "username": "testuser", "password": "secret123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "token" in data
    assert data["username"] == "testuser"


def test_register_duplicate_email(client):
    client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "username": "user1", "password": "pass123"},
    )
    response = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "username": "user2", "password": "pass456"},
    )
    assert response.status_code == 409
    assert "already taken" in response.json()["detail"]


def test_register_duplicate_username(client):
    client.post(
        "/api/auth/register",
        json={"email": "a@example.com", "username": "sameuser", "password": "pass123"},
    )
    response = client.post(
        "/api/auth/register",
        json={"email": "b@example.com", "username": "sameuser", "password": "pass456"},
    )
    assert response.status_code == 409
    assert "already taken" in response.json()["detail"]


def test_login_success(client):
    client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "username": "testuser", "password": "secret123"},
    )
    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "secret123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["username"] == "testuser"


def test_login_wrong_password(client):
    client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "username": "testuser", "password": "secret123"},
    )
    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_login_nonexistent_email(client):
    response = client.post(
        "/api/auth/login",
        json={"email": "nonexistent@example.com", "password": "pass123"},
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_register_missing_fields(client):
    response = client.post("/api/auth/register", json={"email": "a@b.com"})
    assert response.status_code == 422


def test_login_missing_fields(client):
    response = client.post("/api/auth/login", json={})
    assert response.status_code == 422


def test_token_decode():
    from app.services.auth_service import create_token, decode_token

    token = create_token(42)
    assert decode_token(token) == 42


def test_invalid_token_returns_none():
    from app.services.auth_service import decode_token

    assert decode_token("not.a.valid.token") is None