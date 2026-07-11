from datetime import datetime, timedelta, timezone

from sqlalchemy import Column, Integer, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.config import settings


class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)

    checkout_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    due_date = Column(DateTime, nullable=False)
    return_date = Column(DateTime, nullable=True)
    fine_amount = Column(Float, default=0.0)
    fine_paid = Column(Boolean, default=False)

    item = relationship("LibraryItem", back_populates="loans")
    member = relationship("Member", back_populates="loans")

    @staticmethod
    def default_due_date() -> datetime:
        return datetime.now(timezone.utc) + timedelta(days=settings.LOAN_PERIOD_DAYS)

    def calculate_fine(self) -> float:
        """Fine accrues per day overdue, computed against return date or now.

        SQLite stores datetimes as timezone-naive strings.  To avoid a
        TypeError when mixing naive (DB) and aware (timezone.utc) datetimes
        we normalise both operands to naive UTC before the subtraction.
        """
        end = self.return_date or datetime.now(timezone.utc)
        # Strip tzinfo from both sides so subtraction always works regardless
        # of whether the DB driver returns naive or aware datetimes.
        end_naive = end.replace(tzinfo=None) if end.tzinfo else end
        due_naive = self.due_date.replace(tzinfo=None) if self.due_date.tzinfo else self.due_date
        overdue_days = max((end_naive - due_naive).days, 0)
        return round(overdue_days * settings.FINE_PER_DAY, 2)

    @property
    def is_overdue(self) -> bool:
        end = self.return_date or datetime.now(timezone.utc)
        end_naive = end.replace(tzinfo=None) if end.tzinfo else end
        due_naive = self.due_date.replace(tzinfo=None) if self.due_date.tzinfo else self.due_date
        return end_naive > due_naive

    @property
    def item_title(self) -> str:
        return self.item.title if self.item else ""
