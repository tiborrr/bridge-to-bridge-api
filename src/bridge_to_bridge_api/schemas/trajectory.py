from uuid import UUID
from pydantic import BaseModel, ConfigDict

class TrajectoryBase(BaseModel):
    name: str
    
    start_bridge_name: str
    start_north_lat: float
    start_north_lng: float
    start_south_lat: float
    start_south_lng: float
    start_direction_bearing: float
    
    finish_bridge_name: str
    finish_north_lat: float
    finish_north_lng: float
    finish_south_lat: float
    finish_south_lng: float
    finish_direction_bearing: float

class TrajectoryCreate(TrajectoryBase):
    pass

class TrajectoryUpdate(TrajectoryBase):
    pass

class TrajectoryResponse(TrajectoryBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
