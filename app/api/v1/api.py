"""Single router that aggregates all v1 endpoint modules."""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, items, loans, reservations

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(items.router)
api_router.include_router(loans.router)
api_router.include_router(reservations.router)
