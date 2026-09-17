"""Unit & Schema Tests for FastAPI Endpoints."""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.model_loader import model_loader


@pytest.fixture(scope="module")
def client():
    # Ensure model is loaded for testing
    model_loader.load()
    with TestClient(app) as test_client:
        yield test_client


def test_health_check_endpoint(client: TestClient):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "model_loaded" in data


def test_predict_single_valid(client: TestClient):
    payload = {
        "district": "Nuwara Eliya",
        "season": "Maha",
        "crop": "Potato",
        "extent_ha": 350.0,
        "year": 2024
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["district"] == "Nuwara Eliya"
    assert data["crop"] == "Potato"
    assert data["predicted_production_mt"] > 0
    assert data["predicted_yield_mt_per_ha"] > 0
    assert "confidence_interval_95" in data
    assert data["confidence_interval_95"]["lower_mt"] <= data["confidence_interval_95"]["upper_mt"]


def test_predict_single_invalid_extent(client: TestClient):
    payload = {
        "district": "Badulla",
        "season": "Yala",
        "crop": "Maize",
        "extent_ha": -50.0,  # Invalid negative extent
        "year": 2024
    }
    response = client.post("/api/v1/predict", json=payload)
    # Should trigger Pydantic validation error (422 Unprocessable Entity)
    assert response.status_code == 422


def test_batch_prediction(client: TestClient):
    payload = {
        "scenarios": [
            {"district": "Kandy", "season": "Maha", "crop": "Kurakkan", "extent_ha": 120.0, "year": 2024},
            {"district": "Matale", "season": "Yala", "crop": "Chili", "extent_ha": 95.0, "year": 2024}
        ]
    }
    response = client.post("/api/v1/predict/batch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert len(data["predictions"]) == 2
    assert data["predictions"][0]["predicted_production_mt"] >= 0


def test_analytics_districts_endpoint(client: TestClient):
    response = client.get("/api/v1/analytics/districts")
    assert response.status_code == 200
    data = response.json()
    assert "districts" in data
    assert len(data["districts"]) > 0


def test_analytics_crops_endpoint(client: TestClient):
    response = client.get("/api/v1/analytics/crops")
    assert response.status_code == 200
    data = response.json()
    assert "crops" in data
    assert "highland_target_crops" in data


def test_analytics_trends_endpoint(client: TestClient):
    response = client.get("/api/v1/analytics/trends?district=Nuwara%20Eliya&crop=Potato")
    assert response.status_code == 200
    data = response.json()
    assert data["district"] == "Nuwara Eliya"
    assert data["crop"] == "Potato"
    assert "data" in data
