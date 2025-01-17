from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)

def test_422():
    response = client.post("/movies/23/conversations",
                           json = {"character_1_id": "bad value", "character_2_id": 0, 
                                   "lines": [
                                    {
                                        "character_id": 0,
                                        "line_text": "string"
                                    }
                                   ]})
    assert response.status_code == 422

def test_posted_one_line():
    response = client.post("movies/0/conversations",
                           json = {"character_1_id": 0, "character_2_id": 1,
                                   "lines": [
                                    {
                                        "character_id": 0,
                                        "line_text": "testing testing"
                                    }
                                   ]})
    response2 = client.get("/characters/?name=BIANCA&limit=50&offset=0&sort=character")
    assert response2.json()[0]["number_of_lines"] >= 98
    assert response.status_code == 200

