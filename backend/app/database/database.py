"""
Database Configuration

This module configures the SQLAlchemy database engine,
session factory, and declarative base for the
Parkinson Disease Detection System.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session


# ==========================================================
# Database Configuration
# ==========================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./parkinson.db"
)

# ==========================================================
# Engine
# ==========================================================

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
    if DATABASE_URL.startswith("sqlite")
    else {},
    echo=False,
    future=True,
)

# ==========================================================
# Session Factory
# ==========================================================

SessionLocal = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
)

# ==========================================================
# Declarative Base
# ==========================================================

Base = declarative_base()

# ==========================================================
# Dependency
# ==========================================================

def get_db():
    """
    FastAPI database dependency.

    Usage:
        db: Session = Depends(get_db)
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

# ==========================================================
# Database Utilities
# ==========================================================

def create_tables():
    """
    Create all database tables.
    """

    Base.metadata.create_all(bind=engine)


def drop_tables():
    """
    Drop all database tables.
    """

    Base.metadata.drop_all(bind=engine)


def recreate_database():
    """
    Drop and recreate all tables.
    """

    drop_tables()
    create_tables()


def database_status():
    """
    Return basic database information.
    """

    return {
        "database_url": DATABASE_URL,
        "engine": str(engine.url),
        "status": "Connected",
    }
