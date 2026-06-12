"""
test_generate_report.py — Tests for POST /generate-report endpoint.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestGenerateReportEndpoint:
    """Tests for POST /generate-report"""

    # ── Happy path ─────────────────────────────────────────────────────────────

    def test_generate_report_returns_200(self, client):
        """Valid topic should return HTTP 200."""
        response = client.post("/generate-report", json={"topic": "Artificial Intelligence"})
        assert response.status_code == 200

    def test_generate_report_contains_topic(self, client):
        """Response should echo back the topic."""
        response = client.post("/generate-report", json={"topic": "Artificial Intelligence"})
        data = response.json()
        assert "topic" in data
        assert data["topic"] == "Artificial Intelligence"

    def test_generate_report_contains_sections(self, client):
        """Response should contain a non-empty sections list."""
        response = client.post("/generate-report", json={"topic": "Artificial Intelligence"})
        data = response.json()
        assert "sections" in data
        assert isinstance(data["sections"], list)
        assert len(data["sections"]) > 0

    def test_generate_report_contains_final_report(self, client):
        """Response should contain a non-empty final_report string."""
        response = client.post("/generate-report", json={"topic": "Artificial Intelligence"})
        data = response.json()
        assert "final_report" in data
        assert isinstance(data["final_report"], str)
        assert len(data["final_report"]) > 0

    def test_generate_report_response_schema(self, client):
        """Response should match the expected schema exactly."""
        response = client.post("/generate-report", json={"topic": "Artificial Intelligence"})
        data = response.json()
        assert set(data.keys()) == {"topic", "sections", "final_report"}

    def test_generate_report_sections_schema(self, client):
        """Each section in response should have name and description."""
        response = client.post("/generate-report", json={"topic": "Artificial Intelligence"})
        data = response.json()
        for section in data["sections"]:
            assert set(section.keys()) == {"name", "description"}
            assert isinstance(section["name"], str)
            assert isinstance(section["description"], str)

    def test_generate_report_final_report_is_markdown(self, client):
        """Final report should contain markdown content."""
        response = client.post("/generate-report", json={"topic": "Artificial Intelligence"})
        data = response.json()
        # Markdown report should have some content
        assert len(data["final_report"]) > 10

    def test_generate_report_sections_count_matches(self, client):
        """Number of sections should be consistent."""
        response = client.post("/generate-report", json={"topic": "Artificial Intelligence"})
        data = response.json()
        assert len(data["sections"]) >= 2

    # ── Validation errors ──────────────────────────────────────────────────────

    def test_generate_report_missing_topic_returns_422(self, client):
        """Missing topic should return HTTP 422."""
        response = client.post("/generate-report", json={})
        assert response.status_code == 422

    def test_generate_report_empty_topic_returns_422(self, client):
        """Empty string topic should return HTTP 422."""
        response = client.post("/generate-report", json={"topic": ""})
        assert response.status_code == 422

    def test_generate_report_null_topic_returns_422(self, client):
        """Null topic should return HTTP 422."""
        response = client.post("/generate-report", json={"topic": None})
        assert response.status_code == 422

    def test_generate_report_integer_topic_returns_422(self, client):
        """Integer topic should return HTTP 422."""
        response = client.post("/generate-report", json={"topic": 999})
        assert response.status_code == 422

    def test_generate_report_no_body_returns_422(self, client):
        """No request body should return HTTP 422."""
        response = client.post("/generate-report")
        assert response.status_code == 422

    def test_generate_report_extra_fields_ignored(self, client):
        """Extra fields in request body should be ignored gracefully."""
        response = client.post(
            "/generate-report",
            json={"topic": "AI", "unknown_field": "value"},
        )
        assert response.status_code == 200

    # ── Edge cases ─────────────────────────────────────────────────────────────

    def test_generate_report_long_topic(self, client):
        """Long topic strings should be handled without error."""
        long_topic = "Machine Learning " * 15
        response = client.post("/generate-report", json={"topic": long_topic})
        assert response.status_code == 200

    def test_generate_report_special_characters(self, client):
        """Topics with special characters should be handled."""
        response = client.post(
            "/generate-report",
            json={"topic": "AI & Ethics: Why it matters in 2025?"},
        )
        assert response.status_code == 200

    def test_generate_report_unicode_topic(self, client):
        """Unicode topics should be handled."""
        response = client.post(
            "/generate-report",
            json={"topic": "人工智能的未来"},
        )
        assert response.status_code == 200

    # ── Graph failure simulation ───────────────────────────────────────────────

    def test_generate_report_graph_failure_returns_500(self, client):
        """If the LangGraph graph fails, endpoint should return HTTP 500."""
        with patch("backend.orchestrator_worker") as mock_graph:
            mock_graph.invoke.side_effect = Exception("Graph execution failed")
            response = client.post("/generate-report", json={"topic": "AI"})
            assert response.status_code == 500

    def test_generate_report_500_has_detail(self, client):
        """HTTP 500 response should include error detail."""
        with patch("backend.orchestrator_worker") as mock_graph:
            mock_graph.invoke.side_effect = Exception("Graph execution failed")
            response = client.post("/generate-report", json={"topic": "AI"})
            data = response.json()
            assert "detail" in data

    def test_generate_report_timeout_returns_500(self, client):
        """Simulated timeout should return HTTP 500."""
        with patch("backend.orchestrator_worker") as mock_graph:
            mock_graph.invoke.side_effect = TimeoutError("Request timed out")
            response = client.post("/generate-report", json={"topic": "AI"})
            assert response.status_code == 500
