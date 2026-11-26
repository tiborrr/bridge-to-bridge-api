import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from bridge_to_bridge_api.core.database import Base


class RaceSession(Base):
    __tablename__ = "race_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    team_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE")
    )
    trajectory_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("trajectories.id", ondelete="CASCADE")
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )  # the user who recorded it

    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    total_time_seconds: Mapped[float] = mapped_column()

    average_speed_kmh: Mapped[float] = mapped_column()
    average_stroke_rate: Mapped[float] = mapped_column()

    wind_conditions: Mapped[str | None] = mapped_column(default=None)
    weather_conditions: Mapped[str | None] = mapped_column(default=None)
