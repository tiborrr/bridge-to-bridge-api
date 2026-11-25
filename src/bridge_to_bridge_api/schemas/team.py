from pydantic import BaseModel, EmailStr
from typing import List, Optional
import uuid
from .user import UserProfile

class TeamBase(BaseModel):
    name: str
    boat_type: str

class TeamCreate(TeamBase):
    pass

class Team(TeamBase):
    id: uuid.UUID

    class Config:
        from_attributes = True

class TeamMemberBase(BaseModel):
    role: str

class TeamMember(TeamMemberBase):
    id: uuid.UUID
    team_id: uuid.UUID
    user_id: uuid.UUID

    class Config:
        from_attributes = True

class InviteRequest(BaseModel):
    email: EmailStr
