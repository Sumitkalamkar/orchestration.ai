"""
test_models.py — Tests for Pydantic request/response models in backend.py.
"""

import pytest
from pydantic import ValidationError


class TestTopicRequest:
    """Tests for TopicRequest model validation."""

    def test_valid_topic(self):
        from backend import TopicRequest
        req = TopicRequest(topic="Artificial Intelligence")
        assert req.topic == "Artificial Intelligence"

    def test_topic_strips_whitespace_not_enforced(self):
        from backend import TopicRequest
        req = TopicRequest(topic="  AI  ")
        assert req.topic == "  AI  "

    def test_empty_topic_raises_validation_error(self):
        from backend import TopicRequest
        with pytest.raises(ValidationError):
            TopicRequest(topic="")

    def test_none_topic_raises_validation_error(self):
        from backend import TopicRequest
        with pytest.raises(ValidationError):
            TopicRequest(topic=None)

    def test_integer_topic_raises_validation_error(self):
        from backend import TopicRequest
        with pytest.raises(ValidationError):
            TopicRequest(topic=123)


class TestSectionOut:
    """Tests for SectionOut model."""

    def test_valid_section(self):
        from backend import SectionOut
        section = SectionOut(name="Introduction", description="Overview of the topic")
        assert section.name == "Introduction"
        assert section.description == "Overview of the topic"

    def test_missing_name_raises_error(self):
        from backend import SectionOut
        with pytest.raises(ValidationError):
            SectionOut(description="Overview")

    def test_missing_description_raises_error(self):
        from backend import SectionOut
        with pytest.raises(ValidationError):
            SectionOut(name="Introduction")


class TestPlanResponse:
    """Tests for PlanResponse model."""

    def test_valid_plan_response(self):
        from backend import PlanResponse, SectionOut
        response = PlanResponse(sections=[
            SectionOut(name="Intro", description="Overview"),
            SectionOut(name="Conclusion", description="Summary"),
        ])
        assert len(response.sections) == 2

    def test_empty_sections_list(self):
        from backend import PlanResponse
        response = PlanResponse(sections=[])
        assert response.sections == []


class TestReportResponse:
    """Tests for ReportResponse model."""

    def test_valid_report_response(self):
        from backend import ReportResponse, SectionOut
        response = ReportResponse(
            topic="AI",
            sections=[SectionOut(name="Intro", description="Overview")],
            final_report="## Intro\nContent here.",
        )
        assert response.topic == "AI"
        assert len(response.sections) == 1
        assert "Intro" in response.final_report

    def test_missing_topic_raises_error(self):
        from backend import ReportResponse
        with pytest.raises(ValidationError):
            ReportResponse(sections=[], final_report="content")

    def test_missing_final_report_raises_error(self):
        from backend import ReportResponse
        with pytest.raises(ValidationError):
            ReportResponse(topic="AI", sections=[])
