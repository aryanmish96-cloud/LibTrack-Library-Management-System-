from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.item import LibraryItem
from app.repositories.item_repository import ItemRepository
from app.schemas.item import BookCreate, EBookCreate, JournalCreate


class CatalogService:
    def __init__(self, db: Session):
        self.repo = ItemRepository(db)

    def add_book(self, data: BookCreate) -> LibraryItem:
        return self.repo.create_book(data.model_dump())

    def add_ebook(self, data: EBookCreate) -> LibraryItem:
        return self.repo.create_ebook(data.model_dump())

    def add_journal(self, data: JournalCreate) -> LibraryItem:
        return self.repo.create_journal(data.model_dump())

    def get_item(self, item_id: int) -> Optional[LibraryItem]:
        return self.repo.get(item_id)

    def search(self, title: Optional[str] = None, exact: bool = False) -> List[LibraryItem]:
        if not title:
            return self.repo.list_all()
        if exact:
            result = self.repo.search_by_title_exact(title)
            return [result] if result else []
        return self.repo.search_by_title_contains(title)

    def alphabetical_catalog(self) -> List[LibraryItem]:
        return self.repo.list_alphabetical()

    def title_range(self, start: str, end: str) -> List[LibraryItem]:
        return self.repo.title_range(start, end)
