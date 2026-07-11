from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.member import Member, Role

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_member(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Member:
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")

    member = db.query(Member).filter(Member.id == int(payload["sub"])).first()
    if member is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Member not found")
    return member


def require_admin(member: Member = Depends(get_current_member)) -> Member:
    if member.role != Role.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin privileges required")
    return member
