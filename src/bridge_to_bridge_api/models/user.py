import uuid

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from bridge_to_bridge_api.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    keycloak_id: Mapped[str] = mapped_column(unique=True, index=True)
    email: Mapped[str | None] = mapped_column()
    name: Mapped[str | None] = mapped_column()
    preferred_positions: Mapped[list[str]] = mapped_column(JSON, default=list)
