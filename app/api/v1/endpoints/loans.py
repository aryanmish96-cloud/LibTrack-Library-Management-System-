from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_member, require_admin
from app.models.member import Member
from app.schemas.loan import LoanOut
from app.services.loan_service import LoanService

router = APIRouter(prefix="/loans", tags=["loans"])


@router.post("/checkout/{item_id}", response_model=LoanOut, status_code=201)
def checkout(
    item_id: int,
    db: Session = Depends(get_db),
    current_member: Member = Depends(get_current_member),
):
    """Checkout a catalog item. Returns 409 if no copies are available or the
    member already has an active loan for the same item."""
    return LoanService(db).checkout(item_id, current_member.id)


@router.post("/{loan_id}/return", response_model=LoanOut)
def return_item(
    loan_id: int,
    db: Session = Depends(get_db),
    current_member: Member = Depends(get_current_member),
):
    """Return a loaned item. Calculates any overdue fine and promotes the
    next waiting reservation to READY status."""
    return LoanService(db).return_item(loan_id)


@router.get("/my", response_model=list[LoanOut])
def my_loans(
    db: Session = Depends(get_db),
    current_member: Member = Depends(get_current_member),
):
    """List all loans (active and historical) for the authenticated member."""
    return LoanService(db).member_loans(current_member.id)


@router.get("/overdue", response_model=list[LoanOut])
def overdue_loans(
    db: Session = Depends(get_db),
    _: Member = Depends(require_admin),
):
    """Admin-only: list all currently overdue loans."""
    return LoanService(db).overdue_loans()
