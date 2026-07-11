"""Tests for registration and login endpoints."""


def test_register_success(client):
    resp = client.post(
        "/api/v1/auth/register",
        json={"name": "Bob", "email": "bob@test.com", "password": "bobpass"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "bob@test.com"
    assert body["role"] == "member"


def test_register_duplicate_email(client):
    payload = {"name": "Dup", "email": "dup@test.com", "password": "pass"}
    client.post("/api/v1/auth/register", json=payload)
    resp = client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 400


def test_login_success(client):
    client.post(
        "/api/v1/auth/register",
        json={"name": "Carol", "email": "carol@test.com", "password": "carolpass"},
    )
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "carol@test.com", "password": "carolpass"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client):
    client.post(
        "/api/v1/auth/register",
        json={"name": "Dave", "email": "dave@test.com", "password": "davepass"},
    )
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "dave@test.com", "password": "wrongpass"},
    )
    assert resp.status_code == 401
