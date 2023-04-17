from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)

def test_404():
    response = client.get("/characters/490300")
    assert response.status_code == 404