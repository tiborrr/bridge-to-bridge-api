import uuid
from sqlalchemy.orm import Mapped, mapped_column

from bridge_to_bridge_api.core.database import Base

class Trajectory(Base):
    __tablename__ = "trajectories"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    name: Mapped[str] = mapped_column(index=True)
    
    start_bridge_name: Mapped[str]
    start_north_lat: Mapped[float]
    start_north_lng: Mapped[float]
    start_south_lat: Mapped[float]
    start_south_lng: Mapped[float]
    start_direction_bearing: Mapped[float]
    
    finish_bridge_name: Mapped[str]
    finish_north_lat: Mapped[float]
    finish_north_lng: Mapped[float]
    finish_south_lat: Mapped[float]
    finish_south_lng: Mapped[float]
    finish_direction_bearing: Mapped[float]
