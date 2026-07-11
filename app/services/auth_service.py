from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token
from app.models.member import Member
from app.schemas.auth import MemberCreate, LoginRequest


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, data: MemberCreate) -> Member:
        existing = self.db.query(Member).filter(Member.email == data.email).first()
        if existing:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")

        member = Member(
            name=data.name,
            email=data.email,
            hashed_password=hash_password(data.password),
        )
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        return member

    def login(self, data: LoginRequest) -> str:
        member = self.db.query(Member).filter(Member.email == data.email).first()
        if not member or not verify_password(data.password, member.hashed_password):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password")

        return create_access_token(subject=str(member.id), role=member.role.value)
