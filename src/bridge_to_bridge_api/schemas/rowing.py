from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TeamInfo(BaseModel):
    id: str
    name: str
    boat_type: str

class LeaderboardEntry(BaseModel):
    position: int
    team: TeamInfo
    wind_conditions: str
    weather_conditions: str
    time_str: str

class LiveTelemetry(BaseModel):
    speed_kmh: float
    stroke_rate: int
    heart_rate: int
    distance_km: float
    time_lead_seconds: int
    user_progress_percent: int
    opponent_progress_percent: int
    opponent: TeamInfo

class HistorySession(BaseModel):
    id: str
    date: datetime
    segment_name: str
    time_str: str
    average_speed_kmh: float
    average_stroke_rate: int
    
class RaceSessionCreate(BaseModel):
    team_id: str
    trajectory_id: str
    start_time: datetime
    end_time: datetime
    total_time_seconds: float
    average_speed_kmh: float
    average_stroke_rate: float
