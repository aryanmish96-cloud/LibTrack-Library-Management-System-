from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class LoanOut(BaseModel):
    id: int
    item_id: int
    member_id: int
    checkout_date: datetime
    due_date: datetime
    return_date: Optional[datetime]
    fine_amount: float
    fine_paid: bool
    is_overdue: bool
    item_title: Optional[str] = None

    class Config:
        from_attributes = True


class ReservationOut(BaseModel):
    id: int
    item_id: int
    member_id: int
    reservation_date: datetime
    status: str
    queue_position: int
    item_title: Optional[str] = None

    class Config:
        from_attributes = True
