from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from bridge_to_bridge_api.core.config import get_settings


@lru_cache
def get_engine():
    settings = get_settings()
    database_url = settings.DATABASE_URL.replace(
        "postgresql://", "postgresql+psycopg://"
    )
    connect_args = (
        {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    )
    return create_engine(database_url, pool_pre_ping=True, connect_args=connect_args)


@lru_cache
def get_session_local():
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


class Base(DeclarativeBase):
    pass


def get_db():
    db = get_session_local()()
    try:
        yield db
    finally:
        db.close()
