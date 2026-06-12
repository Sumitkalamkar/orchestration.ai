"""
test_health.py — Tests for the health check endpoint.
"""

import pytest


class TestHealthEndpoint:
    """Tests for GET /health"""

    def test_health_returns_200(self, client):
        """Health endpoint should return HTTP 200."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_ok_status(self, client):
        """Health endpoint should return status: ok."""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "ok"

    def test_health_response_is_json(self, client):
        """Health endpoint should return valid JSON."""
        response = client.get("/health")
        assert response.headers["content-type"] == "application/json"

    def test_health_only_accepts_get(self, client):
        """Health endpoint should not accept POST."""
        response = client.post("/health")
        assert response.status_code == 405
