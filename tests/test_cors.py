"""
test_cors.py — Tests for CORS middleware configuration.
"""

import pytest


class TestCORSMiddleware:
    """Tests to ensure CORS is properly configured."""

    def test_cors_allows_options_preflight(self, client):
        """OPTIONS preflight request should return 200."""
        response = client.options(
            "/generate-report",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert response.status_code in [200, 204]

    def test_cors_header_present_on_health(self, client):
        """CORS header should be present on health endpoint response."""
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"},
        )
        assert "access-control-allow-origin" in response.headers

    def test_cors_allows_any_origin(self, client):
        """CORS should allow any origin (wildcard)."""
        response = client.get(
            "/health",
            headers={"Origin": "http://myflutterapp.com"},
        )
        assert response.headers.get("access-control-allow-origin") in ["*", "http://myflutterapp.com"]
