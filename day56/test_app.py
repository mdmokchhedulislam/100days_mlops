"""Unit tests for the CI-pipeline sample app. Run with
`pytest app/` from the repo root."""
import pytest

from app import app as flask_app


@pytest.fixture
def client():
    flask_app.testing = True
    with flask_app.test_client() as c:
        yield c


def test_health_returns_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_predict_flags_high_value_late_night(client):
    resp = client.post("/predict", json={"amount": 999, "hour": 23})
    assert resp.status_code == 200
    assert resp.get_json() == {"is_fraud": 1}


def test_predict_passes_low_value_daytime(client):
    resp = client.post("/predict", json={"amount": 50, "hour": 12})
    assert resp.status_code == 200
    assert resp.get_json() == {"is_fraud": 0}