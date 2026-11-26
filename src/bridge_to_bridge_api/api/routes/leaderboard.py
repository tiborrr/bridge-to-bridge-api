import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from bridge_to_bridge_api.auth.keycloak import get_current_user
from bridge_to_bridge_api.core.database import get_db
from bridge_to_bridge_api.models.race_session import RaceSession
from bridge_to_bridge_api.models.team import Team
from bridge_to_bridge_api.schemas.rowing import LeaderboardEntry, TeamInfo

router = APIRouter()


def format_time(seconds: float) -> str:
    m = int(seconds // 60)
    s = seconds % 60
    return f"{m:02d}:{s:04.1f}"


@router.get("/", response_model=list[LeaderboardEntry])
async def get_leaderboard(
    trajectory_id: str | None = Query(None),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Fetch the best times per team
    stmt = select(
        Team, func.min(RaceSession.total_time_seconds).label("best_time")
    ).join(RaceSession, RaceSession.team_id == Team.id)

    if trajectory_id:
        stmt = stmt.where(RaceSession.trajectory_id == uuid.UUID(trajectory_id))

    stmt = stmt.group_by(Team.id).order_by("best_time").limit(100)

    results = db.execute(stmt).all()

    leaderboard = []
    for index, (team, best_time) in enumerate(results):
        leaderboard.append(
            LeaderboardEntry(
                position=index + 1,
                team=TeamInfo(
                    id=str(team.id), name=team.name, boat_type=team.boat_type
                ),
                # Would need to fetch from the specific session.
                wind_conditions="Onbekend",
                weather_conditions="Onbekend",
                time_str=format_time(best_time),
            )
        )

    return leaderboard
