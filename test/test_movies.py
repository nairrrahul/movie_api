from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)


def test_get_movie():
    response = client.get("/movies/44")
    assert response.status_code == 200

    with open("test/movies/44.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)


def test_movies():
    response = client.get("/movies/")
    assert response.status_code == 200

    with open("test/movies/root.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

# New test case
def test_get_movie2():
    # tests null character in top characters
    response = client.get("/movies/436")
    assert response.status_code == 200

    with open("test/movies/436.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)


def test_sort_filter():
    response = client.get("/movies/?name=big&limit=50&offset=0&sort=rating")
    assert response.status_code == 200

    with open(
        "test/movies/movies-name=big&limit=50&offset=0&sort=rating.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)

# New test case
def test_sort_filter2():
    # Tests going past end of db
    response = client.get("/movies/?limit=250&offset=200&sort=year")
    assert response.status_code == 200

    with open(
        "test/movies/limit=250&offset=200&sort=year.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)


def test_404():
    response = client.get("/movies/1")
    assert response.status_code == 404

#added test

def test_offset_limit():
    response = client.get("/movies/?name=af&limit=5&offset=1&sort=movie_title")
    assert response.status_code == 200

    with open(
        "test/movies/offset_limit.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)
