"""Database engine, session management, and base declarative class."""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from app.core.config import settings

# For SQLite, check_same_thread must be False to allow multi-threaded access in FastAPI
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy declarative models."""
    pass


def get_db() -> Generator[Session, None, None]:
    """Dependency yielding a database session and ensuring it is closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
