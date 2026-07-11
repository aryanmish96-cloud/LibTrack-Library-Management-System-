"""
Custom Binary Search Tree (BST) for LibTrack's catalog search.

WHY THIS EXISTS
----------------
A Python dict (hash map) gives us O(1) average lookup by exact title, which
is great for "find this exact book." But a dict has no sense of ORDER -
you can't ask it "give me every book between 'Emma' and 'Moby Dick'" or
"list all titles alphabetically" without sorting from scratch every time.

A BST keeps items ordered as you insert them, so:
  - Search by exact title:      O(log n) average (vs O(n) scanning a list)
  - In-order traversal:          gives you every title alphabetically, O(n)
  - Range queries (A-M, etc.):   O(log n + k) where k = number of matches

This is the "BST" piece from the original LibTrack design, reimplemented in
Python. The HashMap piece is just a Python dict - see CatalogIndex below,
which uses both together.

HOW IT WORKS (plain English)
------------------------------
Every node holds one item plus a `left` and `right` pointer.
- Inserting: compare the new title to the current node's title.
    smaller -> go left, repeat
    larger  -> go right, repeat
    until you hit an empty spot - that's where the new node goes.
- Searching: same comparison, same left/right walk, until found or you
    fall off the tree (item doesn't exist).

Because each step throws away half the remaining tree (roughly), search
takes O(log n) steps for a balanced tree, instead of checking every item.
"""

from typing import Optional, List, Any


class BSTNode:
    def __init__(self, key: str, value: Any):
        self.key = key          # the field we sort/search by (e.g. book title)
        self.value = value       # the actual item (e.g. a LibraryItem row/dict)
        self.left: Optional["BSTNode"] = None
        self.right: Optional["BSTNode"] = None


class TitleBST:
    """A BST keyed by (lowercased) title, so lookups are case-insensitive."""

    def __init__(self):
        self.root: Optional[BSTNode] = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def insert(self, title: str, value: Any) -> None:
        key = title.lower()
        self.root = self._insert(self.root, key, value)

    def _insert(self, node: Optional[BSTNode], key: str, value: Any) -> BSTNode:
        if node is None:
            self._size += 1
            return BSTNode(key, value)

        if key < node.key:
            node.left = self._insert(node.left, key, value)
        elif key > node.key:
            node.right = self._insert(node.right, key, value)
        else:
            # Title already exists (e.g. multiple copies) - just update value
            node.value = value

        return node

    def search(self, title: str) -> Optional[Any]:
        """O(log n) average case; O(n) worst case for a degenerate/unbalanced tree."""
        key = title.lower()
        return self._search(self.root, key)

    def _search(self, node: Optional[BSTNode], key: str) -> Optional[Any]:
        if node is None:
            return None
        if key == node.key:
            return node.value
        if key < node.key:
            return self._search(node.left, key)
        return self._search(node.right, key)

    def delete(self, title: str) -> None:
        key = title.lower()
        self.root = self._delete(self.root, key)

    def _delete(self, node: Optional[BSTNode], key: str) -> Optional[BSTNode]:
        if node is None:
            return None

        if key < node.key:
            node.left = self._delete(node.left, key)
        elif key > node.key:
            node.right = self._delete(node.right, key)
        else:
            self._size -= 1
            # Case 1: no children
            if node.left is None and node.right is None:
                return None
            # Case 2: one child - replace node with that child
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            # Case 3: two children - find the smallest node in the right
            # subtree (the "in-order successor"), copy its data up, then
            # delete that successor node from the right subtree instead.
            successor = self._find_min(node.right)
            node.key, node.value = successor.key, successor.value
            self._size += 1  # offset the decrement above; successor removal will re-decrement
            node.right = self._delete(node.right, successor.key)

        return node

    def _find_min(self, node: BSTNode) -> BSTNode:
        while node.left is not None:
            node = node.left
        return node

    def in_order(self) -> List[Any]:
        """Returns all values sorted alphabetically by title - O(n)."""
        result: List[Any] = []
        self._in_order(self.root, result)
        return result

    def _in_order(self, node: Optional[BSTNode], result: List[Any]) -> None:
        if node is None:
            return
        self._in_order(node.left, result)
        result.append(node.value)
        self._in_order(node.right, result)

    def range_query(self, start_title: str, end_title: str) -> List[Any]:
        """All items with title between start and end (inclusive), alphabetically."""
        result: List[Any] = []
        self._range(self.root, start_title.lower(), end_title.lower(), result)
        return result

    def _range(self, node, low, high, result):
        if node is None:
            return
        if low < node.key:
            self._range(node.left, low, high, result)
        if low <= node.key <= high:
            result.append(node.value)
        if node.key < high:
            self._range(node.right, low, high, result)


class CatalogIndex:
    """
    Combines a hash map (Python dict) and a BST to give LibTrack both
    lookup strategies without duplicating logic in the service layer.

      - by_isbn / by_id: dict -> O(1) average exact lookup
      - by_title: TitleBST -> O(log n) lookup + alphabetical + range queries
    """

    def __init__(self):
        self.by_id: dict = {}       # HashMap: id -> item
        self.by_isbn: dict = {}     # HashMap: isbn -> item
        self.by_title = TitleBST()  # BST: title -> item

    def add(self, item) -> None:
        self.by_id[item.id] = item
        if getattr(item, "isbn", None):
            self.by_isbn[item.isbn] = item
        self.by_title.insert(item.title, item)

    def remove(self, item) -> None:
        self.by_id.pop(item.id, None)
        if getattr(item, "isbn", None):
            self.by_isbn.pop(item.isbn, None)
        self.by_title.delete(item.title)

    def find_by_title(self, title: str):
        return self.by_title.search(title)

    def find_by_isbn(self, isbn: str):
        return self.by_isbn.get(isbn)

    def alphabetical(self) -> List[Any]:
        return self.by_title.in_order()

    def title_range(self, start: str, end: str) -> List[Any]:
        return self.by_title.range_query(start, end)
