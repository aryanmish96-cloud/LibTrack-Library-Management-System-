# LibTrack

A library management REST API built with **FastAPI**, **SQLAlchemy**, and a custom **Binary Search Tree** catalog index.

---

## Project Overview

LibTrack exposes a clean REST interface for managing a library catalog, member accounts, loans, and reservations. The catalog is backed by both a relational database and an in-memory dual-index (BST + hash map), giving the best of both worlds: database durability and in-process search performance.

---

## Architecture

```
app/
├── core/           Config, DB engine, JWT/bcrypt security helpers
├── models/         SQLAlchemy ORM models (polymorphic LibraryItem hierarchy)
├── repositories/   DB + in-memory index layer (only place that touches SQLAlchemy directly)
├── services/       Business logic (CatalogService, LoanService, ReservationService, AuthService)
├── schemas/        Pydantic request/response models
├── api/
│   ├── deps.py     Auth dependency injection (get_current_member, require_admin)
│   └── v1/
│       ├── api.py               Aggregates all routers
│       └── endpoints/
│           ├── auth.py          Register, login
│           ├── items.py         Catalog CRUD + search
│           ├── loans.py         Checkout, return, history, overdue
│           └── reservations.py  Reserve, cancel
└── main.py         FastAPI app, CORS, lifespan startup index rebuild
```

### Why a BST *and* a Hash Map?

| Need | Structure | Complexity |
|---|---|---|
| Lookup by ID / ISBN | Python `dict` (hash map) | O(1) average |
| Exact title lookup | `TitleBST` | O(log n) average |
| Alphabetical listing | BST in-order traversal | O(n) |
| Range query (e.g. A–M) | BST range walk | O(log n + k) |

A plain `dict` has no notion of **order** — to get alphabetical results you'd need to sort the entire catalog on every request (O(n log n)). The BST keeps items ordered on insertion, so in-order traversal is O(n) and range queries are O(log n + k) where k is the result size. Meanwhile the hash maps give O(1) constant-time lookups for the two most common exact-match patterns (by ID and by ISBN), which would be O(log n) through the BST.

**Limitation**: the BST is keyed on title; if two distinct items share the same title the second insert overwrites the first node. In practice titles are unique enough that this is acceptable; a production system would key on `(title, id)` tuples.

---

## Setup

### Local (virtual environment)

```bash
git clone <repo-url>
cd libtrack
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt

# Apply database migrations
alembic upgrade head

# Start the development server
uvicorn app.main:app --reload
```

The interactive docs are available at http://localhost:8000/docs.

### Docker

```bash
docker compose up --build
```

This builds the image, runs `alembic upgrade head` inside the container, then starts uvicorn on port 8000.

---

## Running Tests

```bash
pytest -v
```

Tests use an **in-memory SQLite** database with `StaticPool` so every connection within a test shares the same database. The global catalog index is reset between tests to prevent BST state from leaking across test cases.

---

## API Endpoint Reference

### Auth

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | None | Register a new member |
| `POST` | `/api/v1/auth/login` | None | Log in, receive JWT |

### Catalog Items

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/items/books` | Admin | Add a physical book |
| `POST` | `/api/v1/items/ebooks` | Admin | Add an e-book |
| `POST` | `/api/v1/items/journals` | Admin | Add a journal |
| `GET` | `/api/v1/items/search?title=X&exact=true` | None | BST exact or DB substring search |
| `GET` | `/api/v1/items/alphabetical` | None | Full catalog in BST alphabetical order |
| `GET` | `/api/v1/items/range?start=A&end=M` | None | BST range query |
| `GET` | `/api/v1/items/{id}` | None | Get item by ID |

### Loans

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/loans/checkout/{item_id}` | Member | Checkout an item |
| `POST` | `/api/v1/loans/{loan_id}/return` | Member | Return an item (calculates fine) |
| `GET` | `/api/v1/loans/my` | Member | Current member's loan history |
| `GET` | `/api/v1/loans/overdue` | Admin | All currently overdue loans |

### Reservations

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/reservations/{item_id}` | Member | Reserve an item |
| `POST` | `/api/v1/reservations/{id}/cancel` | Member | Cancel a reservation |

---

## Design Decisions

### Checkout Rules

- A member may only hold **one active loan per item** at a time. Attempting a second checkout of the same item returns `409 Conflict`.
- When all copies are checked out, checkout returns `409 Conflict` (`"No copies currently available"`).
- The due date defaults to **14 days** from checkout (`LOAN_PERIOD_DAYS` in `config.py`).

### Fine Calculation

Fines are computed lazily **at return time**:

```
fine = max(0, (return_date - due_date).days) × FINE_PER_DAY
```

`FINE_PER_DAY` defaults to **$0.50**. Fines are stored on the `Loan` row as `fine_amount`; a `fine_paid` boolean tracks settlement (payment endpoint is a future extension).

### Reservation Queue

- Any member may reserve any item regardless of availability.
- Reservations are ordered by `queue_position` (monotonically incrementing count of WAITING reservations for that item at the moment of creation).
- When a loan is returned and a copy becomes free, `LoanService._promote_next_reservation` automatically moves the earliest WAITING reservation to **READY** status, signalling the member that they may now collect the item.
- Cancelling a reservation sets its status to **CANCELLED**; queue positions of remaining members are not recalculated (they keep their relative order).

### Polymorphic Catalog Model

`LibraryItem` uses SQLAlchemy's **joined-table inheritance**:
- `items` table holds shared fields (`title`, `author`, `isbn`, `available_copies`).
- `books`, `ebooks`, and `journals` tables hold type-specific fields joined via FK.
- The `item_type` discriminator column enables polymorphic queries.
