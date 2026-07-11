"""
Pytest fixtures for LibTrack.

Key design decisions
---------------------
* StaticPool: SQLAlchemy's default pool opens a new connection (and therefore a
  new in-memory database) per checkout.  In tests, the TestClient issues
  multiple HTTP requests that each get their own DB session.  Without
  StaticPool those sessions see DIFFERENT in-memory databases, so tables
  created by `create_all` are invisible to the handler that runs later.
  StaticPool ensures every connection — across the whole test — shares the
  exact same single SQLite in-memory database.

* catalog_index reset: the global CatalogIndex lives outside the DB session.
  If we don't clear it between tests, BST entries from test A leak into test B.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.core.database import Base, get_db
from app.main import app
from app.core.security import hash_password
from app.models.member import Member, Role
from app.repositories.item_repository import catalog_index
from app.utils.search_structures import CatalogIndex


# ---------------------------------------------------------------------------
# In-memory engine — StaticPool keeps one shared DB across all connections
# ---------------------------------------------------------------------------
TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Session-scoped client so table creation happens once per test module run
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """Create all tables once for the whole test session."""
    Base.metadata.create_all(bind=TEST_ENGINE)
    yield
    Base.metadata.drop_all(bind=TEST_ENGINE)


@pytest.fixture(autouse=True)
def reset_catalog_index():
    """Clear the global in-memory BST/hashmap between every test."""
    yield
    # Replace the index with a fresh empty one so BST state doesn't bleed across tests
    global catalog_index
    import app.repositories.item_repository as repo_module
    repo_module.catalog_index = CatalogIndex()


@pytest.fixture(scope="session")
def client(create_tables):  # depends on create_tables so tables exist first
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Seed helpers — called from individual fixtures so tests are self-contained
# ---------------------------------------------------------------------------
@pytest.fixture()
def db_session():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def admin_token(client):
    """Register an admin user and return a bearer token."""
    db = TestingSession()
    # Directly insert admin (cannot set role via public API)
    existing = db.query(Member).filter(Member.email == "admin@test.com").first()
    if not existing:
        admin = Member(
            name="Admin",
            email="admin@test.com",
            hashed_password=hash_password("adminpass"),
            role=Role.ADMIN,
        )
        db.add(admin)
        db.commit()
    db.close()

    resp = client.post("/api/v1/auth/login", json={"email": "admin@test.com", "password": "adminpass"})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest.fixture()
def member_token(client):
    """Register a regular member and return a bearer token."""
    resp = client.post(
        "/api/v1/auth/register",
        json={"name": "Alice", "email": "alice@test.com", "password": "alicepass"},
    )
    # 201 on first call, 400 on repeat (already registered) — both are fine
    assert resp.status_code in (201, 400)

    resp = client.post("/api/v1/auth/login", json={"email": "alice@test.com", "password": "alicepass"})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]
