"""
LibTrack application entry point.

Wires together the FastAPI app, CORS middleware, API router, and the
startup event that rebuilds the in-memory BST/hash-map catalog index
from whatever rows are already in the database.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.api.v1.api import api_router
from app.repositories.item_repository import ItemRepository


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup logic before the app begins accepting requests."""
    # Ensure all tables exist (handy in dev; Alembic handles prod migrations).
    Base.metadata.create_all(bind=engine)

    # Populate the in-memory BST + hash-map index from the current DB contents.
    db = SessionLocal()
    try:
        ItemRepository(db).rebuild_index()
    finally:
        db.close()

    yield  # app runs here


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A library management system with a custom BST catalog index.",
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS — adjust origins for production deployments
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
