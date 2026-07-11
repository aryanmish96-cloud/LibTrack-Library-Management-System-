import enum
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.core.database import Base


class ReservationStatus(str, enum.Enum):
    WAITING = "waiting"
    READY = "ready"       # item became available, member has a window to collect it
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    reservation_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(Enum(ReservationStatus), default=ReservationStatus.WAITING)
    queue_position = Column(Integer, nullable=False)

    item = relationship("LibraryItem", back_populates="reservations")
    member = relationship("Member", back_populates="reservations")

    @property
    def item_title(self) -> str:
        return self.item.title if self.item else ""
