"""
Repository layer: the only place that talks directly to SQLAlchemy for
catalog items. Services call this instead of touching the DB session
directly - this is what keeps business logic (services) separate from
persistence details (repositories), a standard layered-architecture pattern.

It also maintains an in-memory CatalogIndex (BST + hash maps) as a fast
search cache on top of the database, rebuilt from the DB on startup and
kept in sync on writes.
"""
from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.item import LibraryItem, Book, EBook, Journal
from app.utils.search_structures import CatalogIndex

# Process-wide search index. In a multi-worker deployment you'd move this to
# Redis or rebuild it per-worker; for a single-process app this is fine.
catalog_index = CatalogIndex()


class ItemRepository:
    def __init__(self, db: Session):
        self.db = db

    def rebuild_index(self) -> None:
        catalog_index.by_id.clear()
        catalog_index.by_isbn.clear()
        catalog_index.by_title = type(catalog_index.by_title)()
        for item in self.db.query(LibraryItem).all():
            catalog_index.add(item)

    def create_book(self, data: dict) -> Book:
        item = Book(**data, available_copies=data["total_copies"])
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        catalog_index.add(item)
        return item

    def create_ebook(self, data: dict) -> EBook:
        item = EBook(**data, available_copies=data["total_copies"])
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        catalog_index.add(item)
        return item

    def create_journal(self, data: dict) -> Journal:
        item = Journal(**data, available_copies=data["total_copies"])
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        catalog_index.add(item)
        return item

    def get(self, item_id: int) -> Optional[LibraryItem]:
        # Use the cache only to check existence; always load through the
        # current session to avoid DetachedInstanceError across requests.
        return self.db.query(LibraryItem).filter(LibraryItem.id == item_id).first()

    def get_by_isbn(self, isbn: str) -> Optional[LibraryItem]:
        # Same rationale as get(): always fetch through the current session.
        return self.db.query(LibraryItem).filter(LibraryItem.isbn == isbn).first()

    def search_by_title_exact(self, title: str) -> Optional[LibraryItem]:
        """O(log n) BST lookup instead of a full table scan."""
        return catalog_index.find_by_title(title)

    def search_by_title_contains(self, query: str) -> List[LibraryItem]:
        """Substring search - falls back to the DB since a BST is keyed on
        full titles, not substrings. A Trie would be the right structure
        for prefix search if this needed to scale further."""
        like = f"%{query}%"
        return (
            self.db.query(LibraryItem)
            .filter(LibraryItem.title.ilike(like))
            .all()
        )

    def list_alphabetical(self) -> List[LibraryItem]:
        return catalog_index.alphabetical()

    def title_range(self, start: str, end: str) -> List[LibraryItem]:
        return catalog_index.title_range(start, end)

    def list_all(self) -> List[LibraryItem]:
        return self.db.query(LibraryItem).all()

    def delete(self, item: LibraryItem) -> None:
        catalog_index.remove(item)
        self.db.delete(item)
        self.db.commit()

    def save(self, item: LibraryItem) -> None:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
