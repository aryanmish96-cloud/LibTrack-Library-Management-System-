from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_member
from app.models.member import Member
from app.schemas.loan import ReservationOut
from app.services.loan_service import ReservationService

router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.get("/my", response_model=list[ReservationOut])
def my_reservations(
    db: Session = Depends(get_db),
    current_member: Member = Depends(get_current_member),
):
    """List all reservations (active and historical) for the authenticated member."""
    return ReservationService(db).member_reservations(current_member.id)


@router.post("/{item_id}", response_model=ReservationOut, status_code=201)
def reserve(
    item_id: int,
    db: Session = Depends(get_db),
    current_member: Member = Depends(get_current_member),
):
    """Place a reservation on a catalog item. The member is added to the
    waiting queue; their position is returned in the response."""
    return ReservationService(db).reserve(item_id, current_member.id)


@router.post("/{reservation_id}/cancel", response_model=ReservationOut)
def cancel_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_member: Member = Depends(get_current_member),
):
    """Cancel an existing reservation. The reservation status is set to
    CANCELLED; queue positions of others are not recalculated."""
    return ReservationService(db).cancel(reservation_id)
