from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from bridge_to_bridge_api.api.routes import (
    dashboard,
    history,
    leaderboard,
    team,
    teams,
    trajectories,
    users,
)
from bridge_to_bridge_api.core.config import get_settings
from bridge_to_bridge_api.core.lifespan import lifespan
from bridge_to_bridge_api.core.logging import setup_logging

setup_logging()

# Database tables are now managed by Alembic migrations

app = FastAPI(
    title="Bridge to Bridge API",
    description="Backend API for Bridge to Bridge app",
    version="0.1.0",
    lifespan=lifespan,
)

settings = get_settings()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/version")
async def get_version():
    import os

    return {
        "version": app.version,
        "build_tag": os.getenv("IMAGE_TAG", "unknown"),
        "environment": os.getenv("ENVIRONMENT", "production"),
    }


app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(
    leaderboard.router, prefix="/api/v1/leaderboard", tags=["leaderboard"]
)
app.include_router(history.router, prefix="/api/v1/history", tags=["history"])
app.include_router(
    trajectories.router, prefix="/api/v1/trajectories", tags=["trajectories"]
)
app.include_router(team.router, prefix="/ws/team", tags=["team_ws"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(teams.router, prefix="/api/v1/teams", tags=["teams"])


def main():
    import uvicorn

    uvicorn.run("bridge_to_bridge_api.main:app", host="0.0.0.0", port=3000, reload=True)


if __name__ == "__main__":
    main()
