from contextlib import asynccontextmanager

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from bridge_to_bridge_api.core.database import Base, get_db
from bridge_to_bridge_api.main import app
from bridge_to_bridge_api.models.trajectory import Trajectory

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

from sqlalchemy.pool import StaticPool

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def seed_db(db):
    if db.query(Trajectory).count() == 0:
        t1 = Trajectory(
            name="Spoorbrug naar Wilhelminabrug",
            start_bridge_name="Spoorbrug",
            start_north_lat=52.255876,
            start_north_lng=6.146477,
            start_south_lat=52.254336,
            start_south_lng=6.148564,
            start_direction_bearing=155.0,
            finish_bridge_name="Wilhelminabrug",
            finish_north_lat=52.253011,
            finish_north_lng=6.155700,
            finish_south_lat=52.251457,
            finish_south_lng=6.157813,
            finish_direction_bearing=150.0,
        )
        db.add(t1)
        db.commit()


@pytest.fixture(scope="session")
def setup_database():
    # Create the database and tables
    Base.metadata.create_all(bind=engine)

    # Seed the database
    db = TestingSessionLocal()
    seed_db(db)
    db.close()

    yield

    # Drop the database tables
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(setup_database):
    # Yield a session for a test
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@asynccontextmanager
async def _no_migrations(_app):
    # The app's lifespan runs Alembic against the configured (Postgres) database;
    # tests use the in-memory SQLite schema created by setup_database instead.
    yield


@pytest.fixture
def client(db_session, monkeypatch):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    monkeypatch.setattr(app.router, "lifespan_context", _no_migrations)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
