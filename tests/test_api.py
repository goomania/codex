"""Integration tests covering the FastAPI sentiment endpoints."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_healthcheck():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_form_submission_round_trip():
    response = client.post("/", data={"text": "What a pleasant surprise."})
    assert response.status_code == 200
    assert "pleasant" in response.text
    assert "Result" in response.text


def test_json_api_returns_expected_shape():
    response = client.post("/api/sentiment", json={"text": "I am unsure about this."})
    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == {"label", "score", "positive", "neutral", "negative"}
    assert payload["label"] in {"positive", "neutral", "negative"}


def test_json_api_validation():
    response = client.post("/api/sentiment", json={"text": ""})
    assert response.status_code == 422
