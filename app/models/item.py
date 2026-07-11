from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class LibraryItem(Base):
    """
    Base class for every catalog item.

    Uses SQLAlchemy's joined-table inheritance so that Book, EBook, and
    Journal each get their own table for type-specific fields, while sharing
    common fields and behavior here. This mirrors the same
    inheritance/polymorphism design used in the Java version of LibTrack,
    translated into Python/SQLAlchemy idioms.
    """
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    author = Column(String, nullable=False, index=True)
    isbn = Column(String, unique=True, index=True, nullable=True)
    total_copies = Column(Integer, default=1, nullable=False)
    available_copies = Column(Integer, default=1, nullable=False)
    item_type = Column(String, nullable=False)  # discriminator column

    loans = relationship("Loan", back_populates="item")
    reservations = relationship("Reservation", back_populates="item")

    __mapper_args__ = {
        "polymorphic_identity": "item",
        "polymorphic_on": item_type,
    }

    def is_available(self) -> bool:
        return self.available_copies > 0

    def checkout(self) -> None:
        if not self.is_available():
            raise ValueError("No copies available for checkout")
        self.available_copies -= 1

    def return_item(self) -> None:
        if self.available_copies >= self.total_copies:
            raise ValueError("All copies already accounted for")
        self.available_copies += 1


class Book(LibraryItem):
    __tablename__ = "books"

    id = Column(Integer, ForeignKey("items.id"), primary_key=True)
    genre = Column(String, nullable=True)
    publisher = Column(String, nullable=True)

    __mapper_args__ = {"polymorphic_identity": "book"}


class EBook(LibraryItem):
    __tablename__ = "ebooks"

    id = Column(Integer, ForeignKey("items.id"), primary_key=True)
    file_format = Column(String, default="PDF")
    download_url = Column(String, nullable=True)

    __mapper_args__ = {"polymorphic_identity": "ebook"}

    def checkout(self) -> None:
        # Digital copies are effectively unlimited unless explicitly licensed
        # per-seat; keep the same interface as physical items for polymorphism.
        super().checkout()


class Journal(LibraryItem):
    __tablename__ = "journals"

    id = Column(Integer, ForeignKey("items.id"), primary_key=True)
    issue_number = Column(Integer, nullable=True)
    volume = Column(Integer, nullable=True)

    __mapper_args__ = {"polymorphic_identity": "journal"}
