"""
Basic tests for the FastAPI backend.
Run with: pytest tests/ -v
"""

from fastapi.testclient import TestClient
from backend import app

client = TestClient(app)


def test_health_check():
    """Test the health endpoint returns ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_generate_report_missing_topic():
    """Test that missing topic returns 422."""
    response = client.post("/generate-report", json={})
    assert response.status_code == 422


def test_plan_sections_missing_topic():
    """Test that missing topic returns 422."""
    response = client.post("/plan-sections", json={})
    assert response.status_code == 422
