from fastapi.testclient import TestClient

def test_team_websocket(client: TestClient):
    team_id = "test_team_123"
    with client.websocket_connect(f"/ws/team/{team_id}") as websocket:
        # Simulate stroke seat sending data
        payload = {
            "role": "stroke",
            "spm": 34,
            "catch_time": 1000
        }
        websocket.send_json(payload)
        
        # We expect to receive a team_update response
        response = websocket.receive_json()
        assert response["type"] == "team_update"
        assert response["stroke_spm"] == 34
        assert "sync_score" in response
