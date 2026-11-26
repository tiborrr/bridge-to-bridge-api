import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from bridge_to_bridge_api.auth.keycloak import get_current_user
from bridge_to_bridge_api.core.database import get_db
from bridge_to_bridge_api.models.trajectory import Trajectory
from bridge_to_bridge_api.schemas.trajectory import (
    TrajectoryCreate,
    TrajectoryResponse,
    TrajectoryUpdate,
)

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/", response_model=list[TrajectoryResponse])
def get_trajectories(db: Session = Depends(get_db)):
    """Retrieve all active trajectories."""
    trajectories = db.execute(select(Trajectory)).scalars().all()
    return trajectories


@router.get("/{trajectory_id}", response_model=TrajectoryResponse)
def get_trajectory(trajectory_id: uuid.UUID, db: Session = Depends(get_db)):
    """Retrieve a specific trajectory by ID."""
    db_trajectory = db.get(Trajectory, trajectory_id)
    if not db_trajectory:
        raise HTTPException(status_code=404, detail="Trajectory not found")
    return db_trajectory


@router.post(
    "/", response_model=TrajectoryResponse, status_code=status.HTTP_201_CREATED
)
def create_trajectory(trajectory: TrajectoryCreate, db: Session = Depends(get_db)):
    """Create a new trajectory."""
    db_trajectory = Trajectory(**trajectory.model_dump())
    db.add(db_trajectory)
    db.commit()
    db.refresh(db_trajectory)
    return db_trajectory


@router.put("/{trajectory_id}", response_model=TrajectoryResponse)
def update_trajectory(
    trajectory_id: uuid.UUID,
    trajectory: TrajectoryUpdate,
    db: Session = Depends(get_db),
):
    """Update an existing trajectory."""
    db_trajectory = db.get(Trajectory, trajectory_id)
    if not db_trajectory:
        raise HTTPException(status_code=404, detail="Trajectory not found")

    for key, value in trajectory.model_dump().items():
        setattr(db_trajectory, key, value)

    db.commit()
    db.refresh(db_trajectory)
    return db_trajectory


@router.delete("/{trajectory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trajectory(trajectory_id: uuid.UUID, db: Session = Depends(get_db)):
    """Delete a trajectory."""
    db_trajectory = db.get(Trajectory, trajectory_id)
    if not db_trajectory:
        raise HTTPException(status_code=404, detail="Trajectory not found")

    db.delete(db_trajectory)
    db.commit()
    return None
