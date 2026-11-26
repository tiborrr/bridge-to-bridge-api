import uuid

from pydantic import BaseModel


class UserProfileBase(BaseModel):
    name: str | None = None
    preferred_positions: list[str] = []


class UserProfileUpdate(UserProfileBase):
    pass


class UserProfile(UserProfileBase):
    id: uuid.UUID
    keycloak_id: str
    email: str | None = None

    class Config:
        from_attributes = True
