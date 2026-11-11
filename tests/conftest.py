
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db

# Import models so SQLAlchemy registers their tables.
from app.models.user import User
from app.models.job import Job
from app.models.application import Application


# Separate in-memory database for tests.
TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# Create a fresh database for each test.
@pytest.fixture()
def db():
    Base.metadata.create_all(bind=engine)

    database = TestingSessionLocal()

    try:
        yield database
    finally:
        database.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def db_session(db):
    return db

# Replace the real database dependency.
@pytest.fixture()
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

