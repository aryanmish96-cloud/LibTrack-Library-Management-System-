from datetime import datetime
from pydantic import BaseModel, EmailStr


class MemberCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class MemberOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    membership_date: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
