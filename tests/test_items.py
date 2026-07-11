"""Tests for catalog item endpoints and BST correctness."""
import pytest


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Creation — admin-only enforcement
# ---------------------------------------------------------------------------

def test_admin_can_create_book(client, admin_token):
    resp = client.post(
        "/api/v1/items/books",
        json={"title": "Clean Code", "author": "Martin", "total_copies": 3},
        headers=_auth_header(admin_token),
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "Clean Code"
    assert body["available_copies"] == 3
    assert body["item_type"] == "book"


def test_non_admin_create_book_is_403(client, member_token):
    resp = client.post(
        "/api/v1/items/books",
        json={"title": "Hacker News Book", "author": "Someone", "total_copies": 1},
        headers=_auth_header(member_token),
    )
    assert resp.status_code == 403


def test_admin_can_create_ebook(client, admin_token):
    resp = client.post(
        "/api/v1/items/ebooks",
        json={"title": "Python Tricks", "author": "Bader", "total_copies": 10, "file_format": "EPUB"},
        headers=_auth_header(admin_token),
    )
    assert resp.status_code == 201
    assert resp.json()["item_type"] == "ebook"


def test_admin_can_create_journal(client, admin_token):
    resp = client.post(
        "/api/v1/items/journals",
        json={"title": "Nature Vol 1", "author": "Various", "total_copies": 2, "volume": 1},
        headers=_auth_header(admin_token),
    )
    assert resp.status_code == 201
    assert resp.json()["item_type"] == "journal"


# ---------------------------------------------------------------------------
# BST exact-match search
# ---------------------------------------------------------------------------

def test_exact_title_search(client, admin_token):
    client.post(
        "/api/v1/items/books",
        json={"title": "Refactoring", "author": "Fowler", "total_copies": 1},
        headers=_auth_header(admin_token),
    )
    resp = client.get("/api/v1/items/search?title=Refactoring&exact=true")
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) >= 1
    assert any(r["title"] == "Refactoring" for r in results)


def test_exact_title_search_case_insensitive(client, admin_token):
    # Seed our own book so this test is self-contained (catalog index is reset
    # between tests, so we cannot depend on state from test_exact_title_search)
    client.post(
        "/api/v1/items/books",
        json={"title": "Refactoring Case Test", "author": "Fowler", "total_copies": 1},
        headers=_auth_header(admin_token),
    )
    resp = client.get("/api/v1/items/search?title=refactoring+case+test&exact=true")
    assert resp.status_code == 200
    results = resp.json()
    assert any(r["title"] == "Refactoring Case Test" for r in results)


def test_exact_title_search_no_match(client):
    resp = client.get("/api/v1/items/search?title=Nonexistent+Book+XYZ&exact=true")
    assert resp.status_code == 200
    assert resp.json() == []


# ---------------------------------------------------------------------------
# BST alphabetical listing
# ---------------------------------------------------------------------------

def test_alphabetical_order(client, admin_token):
    # Seed several books whose titles span A-Z
    for title, author in [("Zebra Tales", "ZA"), ("Apple Stories", "AA"), ("Mango Diaries", "MA")]:
        client.post(
            "/api/v1/items/books",
            json={"title": title, "author": author, "total_copies": 1},
            headers=_auth_header(admin_token),
        )
    resp = client.get("/api/v1/items/alphabetical")
    assert resp.status_code == 200
    titles = [item["title"].lower() for item in resp.json()]
    assert titles == sorted(titles), f"Titles not sorted: {titles}"


# ---------------------------------------------------------------------------
# BST range query
# ---------------------------------------------------------------------------

def test_title_range_query(client, admin_token):
    resp = client.get("/api/v1/items/range?start=A&end=N")
    assert resp.status_code == 200
    results = resp.json()
    # Every returned title must fall in the [A, N] alphabetical range
    for item in results:
        assert item["title"].lower() >= "a"
        assert item["title"].lower() <= "n"
