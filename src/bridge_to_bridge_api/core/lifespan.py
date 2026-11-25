import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from alembic.config import Config
from alembic import command
import logging

log = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    log.info("Running database migrations...")
    try:
        alembic_cfg = Config("alembic.ini")
        await asyncio.to_thread(command.upgrade, alembic_cfg, "head")
        log.info("Database migrations complete.")
    except Exception as e:
        log.error(f"Failed to run database migrations: {e}")
        raise
    
    yield
