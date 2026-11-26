from fastapi.testclient import TestClient

from bridge_to_bridge_api.auth.keycloak import get_current_user
from bridge_to_bridge_api.main import app


def test_get_trajectories(client: TestClient):
    app.dependency_overrides[get_current_user] = lambda: {"sub": "test-user-id"}
    response = client.get("/api/v1/trajectories/")
    assert response.status_code == 200
    data = response.json()
    app.dependency_overrides.clear()
    assert len(data) >= 1
    assert data[0]["name"] == "Spoorbrug naar Wilhelminabrug"
    assert data[0]["start_direction_bearing"] == 155.0
    assert data[0]["finish_direction_bearing"] == 150.0
