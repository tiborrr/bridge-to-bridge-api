import json
import logging
from functools import lru_cache

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

router = APIRouter()
logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        # Maps team_id to a list of connected WebSockets
        self.active_connections: dict[str, list[WebSocket]] = {}
        # Stores the stroke seat's SPM to broadcast to others
        self.team_state: dict[str, dict] = {}

    async def connect(self, websocket: WebSocket, team_id: str):
        await websocket.accept()
        if team_id not in self.active_connections:
            self.active_connections[team_id] = []
            self.team_state[team_id] = {"stroke_spm": 0, "catch_timings": []}
        self.active_connections[team_id].append(websocket)
        logger.info(f"Client connected to team {team_id}")

    def disconnect(self, websocket: WebSocket, team_id: str):
        if team_id in self.active_connections:
            self.active_connections[team_id].remove(websocket)
            if not self.active_connections[team_id]:
                del self.active_connections[team_id]
                del self.team_state[team_id]

    async def broadcast_to_team(self, message: dict, team_id: str):
        if team_id in self.active_connections:
            for connection in self.active_connections[team_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message to client: {e}")


@lru_cache
def get_connection_manager() -> ConnectionManager:
    return ConnectionManager()


@router.websocket("/{team_id}")
async def team_websocket(
    websocket: WebSocket,
    team_id: str,
    manager: ConnectionManager = Depends(get_connection_manager),
):
    await manager.connect(websocket, team_id)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                # Example payload:
                # {"role": "stroke", "spm": 32, "catch_time": 123456789}
                # Process the data to calculate sync

                # If this is the stroke seat, update the team state
                if payload.get("role") == "stroke":
                    manager.team_state[team_id]["stroke_spm"] = payload.get("spm", 0)

                # Simple Sync Score logic:
                # In a real app, you'd compare catch_time delta across the team.
                # For this MVP, we just send back a placeholder sync score and the
                # stroke SPM.

                response = {
                    "type": "team_update",
                    "stroke_spm": manager.team_state[team_id].get("stroke_spm", 0),
                    # Placeholder for MVP, could be calculated from catch deltas.
                    "sync_score": 85,
                }

                await manager.broadcast_to_team(response, team_id)

            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        manager.disconnect(websocket, team_id)
