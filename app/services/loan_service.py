from datetime import datetime, timezone
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.loan import Loan
from app.models.reservation import Reservation, ReservationStatus
from app.repositories.item_repository import ItemRepository


class LoanService:
    """
    Encapsulates all lending business rules so routes stay thin and the
    rules stay testable in isolation (see tests/test_loans.py).
    """

    def __init__(self, db: Session):
        self.db = db
        self.repo = ItemRepository(db)

    def checkout(self, item_id: int, member_id: int) -> Loan:
        item = self.repo.get(item_id)
        if item is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Item not found")
        if not item.is_available():
            raise HTTPException(status.HTTP_409_CONFLICT, "No copies currently available")

        # Prevent double-checkout: a member may not hold two active loans for the same item.
        existing = (
            self.db.query(Loan)
            .filter(Loan.item_id == item_id, Loan.member_id == member_id, Loan.return_date.is_(None))
            .first()
        )
        if existing:
            raise HTTPException(status.HTTP_409_CONFLICT, "You already have an active loan for this item")

        item.checkout()
        self.repo.save(item)

        # Fulfill active reservation if it exists
        active_res = (
            self.db.query(Reservation)
            .filter(
                Reservation.item_id == item_id,
                Reservation.member_id == member_id,
                Reservation.status.in_([ReservationStatus.WAITING, ReservationStatus.READY])
            )
            .first()
        )
        if active_res:
            active_res.status = ReservationStatus.FULFILLED
            self.db.add(active_res)

        loan = Loan(
            item_id=item_id,
            member_id=member_id,
            due_date=Loan.default_due_date(),
        )
        self.db.add(loan)
        self.db.commit()
        self.db.refresh(loan)
        return loan

    def return_item(self, loan_id: int) -> Loan:
        loan = self.db.query(Loan).filter(Loan.id == loan_id).first()
        if loan is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Loan not found")
        if loan.return_date is not None:
            raise HTTPException(status.HTTP_409_CONFLICT, "Item already returned")

        loan.return_date = datetime.now(timezone.utc)
        loan.fine_amount = loan.calculate_fine()

        item = self.repo.get(loan.item_id)
        item.return_item()
        self.repo.save(item)

        self.db.add(loan)
        self.db.commit()
        self.db.refresh(loan)

        self._promote_next_reservation(loan.item_id)
        return loan

    def _promote_next_reservation(self, item_id: int) -> None:
        """When a copy frees up, move the earliest waiting reservation to READY."""
        next_res = (
            self.db.query(Reservation)
            .filter(Reservation.item_id == item_id, Reservation.status == ReservationStatus.WAITING)
            .order_by(Reservation.queue_position.asc())
            .first()
        )
        if next_res:
            next_res.status = ReservationStatus.READY
            self.db.add(next_res)
            self.db.commit()

    def member_loans(self, member_id: int) -> List[Loan]:
        return self.db.query(Loan).filter(Loan.member_id == member_id).all()

    def overdue_loans(self) -> List[Loan]:
        now = datetime.now(timezone.utc)
        return (
            self.db.query(Loan)
            .filter(Loan.return_date.is_(None), Loan.due_date < now)
            .all()
        )


class ReservationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ItemRepository(db)

    def reserve(self, item_id: int, member_id: int) -> Reservation:
        item = self.repo.get(item_id)
        if item is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Item not found")

        current_queue = (
            self.db.query(Reservation)
            .filter(Reservation.item_id == item_id, Reservation.status == ReservationStatus.WAITING)
            .count()
        )

        reservation = Reservation(
            item_id=item_id,
            member_id=member_id,
            queue_position=current_queue + 1,
        )
        self.db.add(reservation)
        self.db.commit()
        self.db.refresh(reservation)
        return reservation

    def cancel(self, reservation_id: int) -> Reservation:
        reservation = self.db.query(Reservation).filter(Reservation.id == reservation_id).first()
        if reservation is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Reservation not found")
        reservation.status = ReservationStatus.CANCELLED
        self.db.add(reservation)
        self.db.commit()
        self.db.refresh(reservation)
        return reservation

    def member_reservations(self, member_id: int) -> List[Reservation]:
        return (
            self.db.query(Reservation)
            .filter(Reservation.member_id == member_id)
            .order_by(Reservation.reservation_date.desc())
            .all()
        )
