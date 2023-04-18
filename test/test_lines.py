from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)

def test_404():
    response = client.get("/characters/490300")
    assert response.status_code == 404

def test_get_lines():
    response = client.get("/lines/?text=barrel&limit=6&offset=0&sort=length")
    assert response.status_code == 200

    with open(
        "test/lines/barrel.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)

def test_conversations_by_movie_id():
    response = client.get("/conversations/456")
    assert response.status_code == 200

    with open(
        "test/lines/456.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)

def test_lines_by_conversation_id():
    response = client.get("/lines/25")
    assert response.status_code == 200

    with open(
        "test/lines/25.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)

def test_get_lines_limit_offset():
    response = client.get("lines/?text=help&limit=12&offset=15&sort=movie_title")
    assert response.status_code == 200

    with open(
        "test/lines/offset_limit.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)

def test_invalid_input():
    response = client.get("lines/?text=bar&limit=260&offset=0&sort=movie_title")
    assert response.status_code == 422