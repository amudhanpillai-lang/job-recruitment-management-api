# Import SQLAlchemy components

import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load environment variables from .env
load_dotenv()

# Read database URL from environment.
# Local development uses localhost.
# Docker Compose will override this with the PostgreSQL service hostname.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:root@localhost:5432/job_recruitment"
)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for SQLAlchemy models
Base = declarative_base()


# Database dependency
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
