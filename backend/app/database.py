"""SQLModel engine and session setup."""
from collections.abc import Iterator

from sqlmodel import Session, SQLModel, create_engine

from .config import DATABASE_URL

# SQLite needs check_same_thread=False for FastAPI's threaded request handling.
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)


def init_db() -> None:
    """Create all tables. Safe to call repeatedly."""
    # Import models so SQLModel.metadata knows about them.
    from . import models  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    """FastAPI dependency that yields a DB session."""
    with Session(engine) as session:
        yield session
