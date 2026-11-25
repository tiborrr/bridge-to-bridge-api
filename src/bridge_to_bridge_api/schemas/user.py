from pydantic import BaseModel
from typing import List, Optional
import uuid

class UserProfileBase(BaseModel):
    name: Optional[str] = None
    preferred_positions: List[str] = []

class UserProfileUpdate(UserProfileBase):
    pass

class UserProfile(UserProfileBase):
    id: uuid.UUID
    keycloak_id: str
    email: Optional[str] = None

    class Config:
        from_attributes = True
