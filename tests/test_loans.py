"""Tests for loan and reservation workflows."""
from datetime import datetime, timedelta

import pytest

from app.models.loan import Loan
from tests.conftest import TestingSession


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _create_book(client, admin_token, title="Test Book", copies=2):
    resp = client.post(
        "/api/v1/items/books",
        json={"title": title, "author": "Author", "total_copies": copies},
        headers=_auth_header(admin_token),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


# ---------------------------------------------------------------------------
# Checkout — happy path reduces available_copies
# ---------------------------------------------------------------------------

def test_checkout_reduces_available_copies(client, admin_token, member_token):
    item_id = _create_book(client, admin_token, title="Copies Test Book", copies=2)

    resp = client.post(f"/api/v1/loans/checkout/{item_id}", headers=_auth_header(member_token))
    assert resp.status_code == 201, resp.text
    loan = resp.json()
    assert loan["item_id"] == item_id

    # Fetch the item and verify available_copies went down by 1
    item_resp = client.get(f"/api/v1/items/{item_id}")
    assert item_resp.json()["available_copies"] == 1


# ---------------------------------------------------------------------------
# Double-checkout returns 409
# ---------------------------------------------------------------------------

def test_double_checkout_returns_409(client, admin_token, member_token):
    item_id = _create_book(client, admin_token, title="Double Checkout Book", copies=3)

    # First checkout — must succeed
    r1 = client.post(f"/api/v1/loans/checkout/{item_id}", headers=_auth_header(member_token))
    assert r1.status_code == 201, r1.text

    # Second checkout for SAME item by SAME member — must be 409
    r2 = client.post(f"/api/v1/loans/checkout/{item_id}", headers=_auth_header(member_token))
    assert r2.status_code == 409, r2.text


# ---------------------------------------------------------------------------
# Return — calculates fines correctly for an overdue loan
# ---------------------------------------------------------------------------

def test_return_calculates_overdue_fine(client, admin_token, member_token):
    item_id = _create_book(client, admin_token, title="Overdue Fine Book", copies=1)

    checkout_resp = client.post(
        f"/api/v1/loans/checkout/{item_id}",
        headers=_auth_header(member_token),
    )
    assert checkout_resp.status_code == 201, checkout_resp.text
    loan_id = checkout_resp.json()["id"]

    # Manually backdate the due_date so the loan is 5 days overdue
    db = TestingSession()
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    loan.due_date = datetime.utcnow() - timedelta(days=5)
    db.commit()
    db.close()

    return_resp = client.post(f"/api/v1/loans/{loan_id}/return", headers=_auth_header(member_token))
    assert return_resp.status_code == 200, return_resp.text
    returned = return_resp.json()

    # 5 days * $0.50/day = $2.50
    assert returned["fine_amount"] == pytest.approx(2.50, abs=0.01)
    assert returned["return_date"] is not None


# ---------------------------------------------------------------------------
# Member loan history
# ---------------------------------------------------------------------------

def test_my_loans(client, admin_token, member_token):
    item_id = _create_book(client, admin_token, title="My Loans Book", copies=5)
    client.post(f"/api/v1/loans/checkout/{item_id}", headers=_auth_header(member_token))

    resp = client.get("/api/v1/loans/my", headers=_auth_header(member_token))
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


# ---------------------------------------------------------------------------
# Reservations — place and cancel
# ---------------------------------------------------------------------------

def test_reserve_and_cancel(client, admin_token, member_token):
    item_id = _create_book(client, admin_token, title="Reserve Cancel Book", copies=1)

    # Reserve the item
    res_resp = client.post(f"/api/v1/reservations/{item_id}", headers=_auth_header(member_token))
    assert res_resp.status_code == 201, res_resp.text
    reservation_id = res_resp.json()["id"]
    assert res_resp.json()["status"] == "waiting"

    # Cancel the reservation
    cancel_resp = client.post(
        f"/api/v1/reservations/{reservation_id}/cancel",
        headers=_auth_header(member_token),
    )
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "cancelled"


def test_my_reservations(client, admin_token, member_token):
    item_id = _create_book(client, admin_token, title="My Reservations Book", copies=1)

    # Place a reservation
    res_resp = client.post(f"/api/v1/reservations/{item_id}", headers=_auth_header(member_token))
    assert res_resp.status_code == 201
    
    # Query reservations
    my_res = client.get("/api/v1/reservations/my", headers=_auth_header(member_token))
    assert my_res.status_code == 200
    data = my_res.json()
    assert len(data) >= 1
    assert data[0]["item_id"] == item_id
    assert data[0]["item_title"] == "My Reservations Book"


def test_checkout_fulfills_reservation(client, admin_token, member_token):
    item_id = _create_book(client, admin_token, title="Fulfillment Book", copies=1)

    # Place a reservation
    res_resp = client.post(f"/api/v1/reservations/{item_id}", headers=_auth_header(member_token))
    assert res_resp.status_code == 201
    res_id = res_resp.json()["id"]
    assert res_resp.json()["status"] == "waiting"

    # Checkout the item
    checkout_resp = client.post(f"/api/v1/loans/checkout/{item_id}", headers=_auth_header(member_token))
    assert checkout_resp.status_code == 201
    
    # Check that reservation is now fulfilled
    my_res = client.get("/api/v1/reservations/my", headers=_auth_header(member_token))
    assert my_res.status_code == 200
    data = my_res.json()
    res_record = next(r for r in data if r["id"] == res_id)
    assert res_record["status"] == "fulfilled"
