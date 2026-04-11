"""
JobForge — Database Setup
SQLAlchemy engine for SQLite (dev) and PostgreSQL (prod).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings
import os

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# Build engine with database-specific config
database_url = settings.DATABASE_URL

# SQLite needs check_same_thread, PostgreSQL doesn't
if database_url.startswith("sqlite"):
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        echo=False,
    )
else:
    # PostgreSQL (Railway)
    engine = create_engine(
        database_url,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=300,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency: yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables on startup."""
    from models import Job, BaseResume, ScanSession  # noqa: F401
    Base.metadata.create_all(bind=engine)
