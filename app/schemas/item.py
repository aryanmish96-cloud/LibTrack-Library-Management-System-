from typing import Optional, Literal
from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    title: str
    author: str
    isbn: Optional[str] = None
    total_copies: int = Field(default=1, ge=1)


class BookCreate(ItemBase):
    genre: Optional[str] = None
    publisher: Optional[str] = None


class EBookCreate(ItemBase):
    file_format: str = "PDF"
    download_url: Optional[str] = None


class JournalCreate(ItemBase):
    issue_number: Optional[int] = None
    volume: Optional[int] = None


class ItemOut(BaseModel):
    id: int
    title: str
    author: str
    isbn: Optional[str]
    total_copies: int
    available_copies: int
    item_type: str

    class Config:
        from_attributes = True


class ItemSearchResult(BaseModel):
    results: list[ItemOut]
    count: int
