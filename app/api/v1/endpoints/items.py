from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import require_admin
from app.schemas.item import BookCreate, EBookCreate, JournalCreate, ItemOut
from app.services.catalog_service import CatalogService

router = APIRouter(prefix="/items", tags=["catalog"])


@router.post("/books", response_model=ItemOut, status_code=201)
def add_book(data: BookCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return CatalogService(db).add_book(data)


@router.post("/ebooks", response_model=ItemOut, status_code=201)
def add_ebook(data: EBookCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return CatalogService(db).add_ebook(data)


@router.post("/journals", response_model=ItemOut, status_code=201)
def add_journal(data: JournalCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return CatalogService(db).add_journal(data)


@router.get("/search", response_model=list[ItemOut])
def search_items(
    title: Optional[str] = None,
    exact: bool = False,
    db: Session = Depends(get_db),
):
    """
    exact=true uses the BST for an O(log n) exact-title lookup.
    exact=false (default) does a substring search across the catalog.
    """
    return CatalogService(db).search(title=title, exact=exact)


@router.get("/alphabetical", response_model=list[ItemOut])
def alphabetical_catalog(db: Session = Depends(get_db)):
    """Full catalog sorted alphabetically via BST in-order traversal - O(n)."""
    return CatalogService(db).alphabetical_catalog()


@router.get("/range", response_model=list[ItemOut])
def title_range(start: str, end: str, db: Session = Depends(get_db)):
    """All items with titles between `start` and `end` alphabetically."""
    return CatalogService(db).title_range(start, end)


@router.get("/{item_id}", response_model=ItemOut)
def get_item(item_id: int, db: Session = Depends(get_db)):
    from fastapi import HTTPException
    item = CatalogService(db).get_item(item_id)
    if item is None:
        raise HTTPException(404, "Item not found")
    return item
