"""
Unit tests for TitleBST — exercised directly without going through the HTTP
layer so we can test data-structure correctness in isolation.
"""
import pytest
from app.utils.search_structures import TitleBST


@pytest.fixture()
def bst():
    tree = TitleBST()
    for title, value in [
        ("Moby Dick", {"id": 1}),
        ("Anna Karenina", {"id": 2}),
        ("Zebra Crossing", {"id": 3}),
        ("Emma", {"id": 4}),
        ("Great Expectations", {"id": 5}),
    ]:
        tree.insert(title, value)
    return tree


# ---------------------------------------------------------------------------
# Exact match
# ---------------------------------------------------------------------------

def test_exact_match_found(bst):
    result = bst.search("Moby Dick")
    assert result == {"id": 1}


def test_exact_match_case_insensitive(bst):
    result = bst.search("MOBY DICK")
    assert result == {"id": 1}


def test_exact_match_not_found(bst):
    assert bst.search("War and Peace") is None


# ---------------------------------------------------------------------------
# Alphabetical in-order traversal
# ---------------------------------------------------------------------------

def test_in_order_is_sorted(bst):
    values = bst.in_order()
    # The BST stores lowercased keys; extract IDs in the order returned
    ids = [v["id"] for v in values]
    titles = ["Anna Karenina", "Emma", "Great Expectations", "Moby Dick", "Zebra Crossing"]
    expected_ids = [{"Anna Karenina": 2, "Emma": 4, "Great Expectations": 5, "Moby Dick": 1, "Zebra Crossing": 3}[t] for t in titles]
    assert ids == expected_ids


def test_in_order_length(bst):
    assert len(bst.in_order()) == 5


# ---------------------------------------------------------------------------
# Range query
# ---------------------------------------------------------------------------

def test_range_includes_boundaries(bst):
    # "Emma" and "Moby Dick" should both appear in [E, M]
    results = bst.range_query("Emma", "Moby Dick")
    ids = {v["id"] for v in results}
    assert 4 in ids  # Emma
    assert 1 in ids  # Moby Dick


def test_range_excludes_outside(bst):
    # [A, E] should NOT include Great Expectations (G > E), Moby Dick, Zebra
    results = bst.range_query("A", "E")
    ids = {v["id"] for v in results}
    assert 5 not in ids   # Great Expectations
    assert 1 not in ids   # Moby Dick
    assert 3 not in ids   # Zebra Crossing


def test_range_empty(bst):
    # [N, P] — nothing in the tree falls here
    results = bst.range_query("N", "P")
    assert results == []


# ---------------------------------------------------------------------------
# Insert & delete
# ---------------------------------------------------------------------------

def test_insert_increases_size(bst):
    before = len(bst)
    bst.insert("New Book", {"id": 99})
    assert len(bst) == before + 1


def test_delete_removes_item(bst):
    bst.delete("Emma")
    assert bst.search("Emma") is None


def test_delete_nonexistent_is_safe(bst):
    """Deleting a missing key should not raise."""
    bst.delete("This Does Not Exist")
