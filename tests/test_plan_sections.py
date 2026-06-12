"""
test_plan_sections.py — Tests for POST /plan-sections endpoint.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestPlanSectionsEndpoint:
    """Tests for POST /plan-sections"""

    # ── Happy path ─────────────────────────────────────────────────────────────

    def test_plan_sections_returns_200(self, client):
        """Valid topic should return HTTP 200."""
        response = client.post("/plan-sections", json={"topic": "Artificial Intelligence"})
        assert response.status_code == 200

    def test_plan_sections_returns_list(self, client):
        """Response should contain a sections list."""
        response = client.post("/plan-sections", json={"topic": "Artificial Intelligence"})
        data = response.json()
        assert "sections" in data
        assert isinstance(data["sections"], list)

    def test_plan_sections_not_empty(self, client):
        """Sections list should not be empty for a valid topic."""
        response = client.post("/plan-sections", json={"topic": "Artificial Intelligence"})
        data = response.json()
        assert len(data["sections"]) > 0

    def test_plan_sections_each_has_name(self, client):
        """Every section should have a non-empty name."""
        response = client.post("/plan-sections", json={"topic": "Artificial Intelligence"})
        data = response.json()
        for section in data["sections"]:
            assert "name" in section
            assert isinstance(section["name"], str)
            assert len(section["name"]) > 0

    def test_plan_sections_each_has_description(self, client):
        """Every section should have a non-empty description."""
        response = client.post("/plan-sections", json={"topic": "Artificial Intelligence"})
        data = response.json()
        for section in data["sections"]:
            assert "description" in section
            assert isinstance(section["description"], str)
            assert len(section["description"]) > 0

    def test_plan_sections_response_schema(self, client):
        """Response should match the expected schema exactly."""
        response = client.post("/plan-sections", json={"topic": "Artificial Intelligence"})
        data = response.json()
        assert set(data.keys()) == {"sections"}
        for section in data["sections"]:
            assert set(section.keys()) == {"name", "description"}

    # ── Validation errors ──────────────────────────────────────────────────────

    def test_plan_sections_missing_topic_returns_422(self, client):
        """Missing topic field should return HTTP 422."""
        response = client.post("/plan-sections", json={})
        assert response.status_code == 422

    def test_plan_sections_empty_topic_returns_422(self, client):
        """Empty string topic should return HTTP 422."""
        response = client.post("/plan-sections", json={"topic": ""})
        assert response.status_code == 422

    def test_plan_sections_null_topic_returns_422(self, client):
        """Null topic should return HTTP 422."""
        response = client.post("/plan-sections", json={"topic": None})
        assert response.status_code == 422

    def test_plan_sections_wrong_type_returns_422(self, client):
        """Non-string topic should return HTTP 422."""
        response = client.post("/plan-sections", json={"topic": 12345})
        assert response.status_code == 422

    def test_plan_sections_empty_body_returns_422(self, client):
        """Empty request body should return HTTP 422."""
        response = client.post("/plan-sections")
        assert response.status_code == 422

    def test_plan_sections_extra_fields_ignored(self, client):
        """Extra fields in request body should be ignored gracefully."""
        response = client.post(
            "/plan-sections",
            json={"topic": "Artificial Intelligence", "extra_field": "ignored"},
        )
        assert response.status_code == 200

    # ── Edge cases ─────────────────────────────────────────────────────────────

    def test_plan_sections_long_topic(self, client):
        """Long topic strings should be handled without error."""
        long_topic = "Artificial Intelligence " * 20
        response = client.post("/plan-sections", json={"topic": long_topic})
        assert response.status_code == 200

    def test_plan_sections_special_characters(self, client):
        """Topics with special characters should be handled."""
        response = client.post(
            "/plan-sections",
            json={"topic": "AI & ML: Future of Human-Computer Interaction?"},
        )
        assert response.status_code == 200

    # ── LLM failure simulation ─────────────────────────────────────────────────

    def test_plan_sections_llm_failure_returns_500(self, client):
        """If the LLM/planner fails, the endpoint should return HTTP 500."""
        with patch("backend.planner") as mock_planner:
            mock_planner.invoke.side_effect = Exception("LLM service unavailable")
            response = client.post("/plan-sections", json={"topic": "AI"})
            assert response.status_code == 500

    def test_plan_sections_500_has_detail(self, client):
        """HTTP 500 response should include an error detail field."""
        with patch("backend.planner") as mock_planner:
            mock_planner.invoke.side_effect = Exception("LLM service unavailable")
            response = client.post("/plan-sections", json={"topic": "AI"})
            data = response.json()
            assert "detail" in data
