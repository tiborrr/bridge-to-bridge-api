from fastapi import APIRouter, Depends

from bridge_to_bridge_api.auth.keycloak import get_current_user
from bridge_to_bridge_api.schemas.rowing import LiveTelemetry, TeamInfo

router = APIRouter()


@router.get("/live", response_model=LiveTelemetry)
async def get_live_dashboard(user: dict = Depends(get_current_user)):
    # Return dummy data matching the Stitch design
    return LiveTelemetry(
        speed_kmh=14.2,
        stroke_rate=32,
        heart_rate=164,
        distance_km=2.8,
        time_lead_seconds=-4,  # 4 seconds behind/ahead
        user_progress_percent=78,
        opponent_progress_percent=72,
        opponent=TeamInfo(id="freya", name="Team Freya", boat_type="Visbyvaarder"),
    )
