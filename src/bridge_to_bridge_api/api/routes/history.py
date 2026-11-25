from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
import uuid

from bridge_to_bridge_api.core.database import get_db
from bridge_to_bridge_api.schemas.rowing import HistorySession, RaceSessionCreate
from bridge_to_bridge_api.models.race_session import RaceSession
from bridge_to_bridge_api.models.trajectory import Trajectory
from bridge_to_bridge_api.models.user import User
from bridge_to_bridge_api.auth.keycloak import get_current_user

router = APIRouter()

def format_time(seconds: float) -> str:
    m = int(seconds // 60)
    s = seconds % 60
    return f"{m:02d}:{s:04.1f}"

@router.get("/", response_model=List[HistorySession])
async def get_history(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    keycloak_id = user["sub"]
    db_user = db.scalar(select(User).where(User.keycloak_id == keycloak_id))
    if not db_user:
        return []
        
    stmt = (
        select(RaceSession, Trajectory)
        .join(Trajectory, RaceSession.trajectory_id == Trajectory.id)
        .where(RaceSession.user_id == db_user.id)
        .order_by(RaceSession.end_time.desc())
    )
    results = db.execute(stmt).all()
    
    return [
        HistorySession(
            id=str(session.id),
            date=session.end_time,
            segment_name=trajectory.name,
            time_str=format_time(session.total_time_seconds),
            average_speed_kmh=session.average_speed_kmh,
            average_stroke_rate=int(session.average_stroke_rate)
        )
        for session, trajectory in results
    ]

@router.post("/", response_model=HistorySession)
async def create_history(
    data: RaceSessionCreate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    keycloak_id = user["sub"]
    db_user = db.scalar(select(User).where(User.keycloak_id == keycloak_id))
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    trajectory = db.get(Trajectory, uuid.UUID(data.trajectory_id))
    if not trajectory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trajectory not found")

    new_session = RaceSession(
        team_id=uuid.UUID(data.team_id),
        trajectory_id=uuid.UUID(data.trajectory_id),
        user_id=db_user.id,
        start_time=data.start_time,
        end_time=data.end_time,
        total_time_seconds=data.total_time_seconds,
        average_speed_kmh=data.average_speed_kmh,
        average_stroke_rate=data.average_stroke_rate
    )
    
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    return HistorySession(
        id=str(new_session.id),
        date=new_session.end_time,
        segment_name=trajectory.name,
        time_str=format_time(new_session.total_time_seconds),
        average_speed_kmh=new_session.average_speed_kmh,
        average_stroke_rate=int(new_session.average_stroke_rate)
    )
