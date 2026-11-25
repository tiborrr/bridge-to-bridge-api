from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from bridge_to_bridge_api.core.config import get_settings

from functools import lru_cache

@lru_cache()
def get_engine():
    settings = get_settings()
    SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")
    connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
    return create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)

@lru_cache()
def get_session_local():
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())

class Base(DeclarativeBase):
    pass

def get_db():
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
