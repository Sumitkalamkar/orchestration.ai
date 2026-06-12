"""
test_graph.py — Unit tests for graph.py nodes and state logic.
All LLM calls are mocked — no real API calls made.
"""

import pytest
import operator
from unittest.mock import MagicMock, patch
from typing import Annotated


class TestOrchestratorNode:
    """Tests for the orchestrator node in graph.py"""

    def test_orchestrator_returns_sections_key(self):
        """Orchestrator node should return a dict with 'sections' key."""
        mock_section = MagicMock()
        mock_section.name = "Introduction"
        mock_section.description = "Overview"

        mock_output = MagicMock()
        mock_output.sections = [mock_section]

        with patch("graph.planner") as mock_planner:
            mock_planner.invoke.return_value = mock_output
            from graph import orchestrator
            result = orchestrator({"topic": "AI", "sections": [], "completed_sections": [], "final_report": ""})
            assert "sections" in result

    def test_orchestrator_returns_list_of_sections(self):
        """Orchestrator node should return a list under 'sections'."""
        mock_section = MagicMock()
        mock_section.name = "Introduction"
        mock_section.description = "Overview"

        mock_output = MagicMock()
        mock_output.sections = [mock_section]

        with patch("graph.planner") as mock_planner:
            mock_planner.invoke.return_value = mock_output
            from graph import orchestrator
            result = orchestrator({"topic": "AI", "sections": [], "completed_sections": [], "final_report": ""})
            assert isinstance(result["sections"], list)

    def test_orchestrator_passes_topic_to_planner(self):
        """Orchestrator should call planner with the correct topic."""
        mock_output = MagicMock()
        mock_output.sections = []

        with patch("graph.planner") as mock_planner:
            mock_planner.invoke.return_value = mock_output
            from graph import orchestrator
            orchestrator({"topic": "Quantum Computing", "sections": [], "completed_sections": [], "final_report": ""})
            mock_planner.invoke.assert_called_once()
            call_args = mock_planner.invoke.call_args[0][0]
            # Check topic is in one of the messages
            messages_content = " ".join([m.content for m in call_args])
            assert "Quantum Computing" in messages_content


class TestLLMCallNode:
    """Tests for the llm_call worker node in graph.py"""

    def test_llm_call_returns_completed_sections_key(self):
        """llm_call node should return dict with 'completed_sections' key."""
        mock_response = MagicMock()
        mock_response.content = "## Introduction\nContent here."

        mock_section = MagicMock()
        mock_section.name = "Introduction"
        mock_section.description = "Overview of the topic"

        with patch("graph.llm") as mock_llm:
            mock_llm.invoke.return_value = mock_response
            from graph import llm_call
            result = llm_call({"section": mock_section, "completed_sections": []})
            assert "completed_sections" in result

    def test_llm_call_returns_list(self):
        """llm_call should return a list under 'completed_sections'."""
        mock_response = MagicMock()
        mock_response.content = "## Section\nContent."

        mock_section = MagicMock()
        mock_section.name = "Background"
        mock_section.description = "Historical context"

        with patch("graph.llm") as mock_llm:
            mock_llm.invoke.return_value = mock_response
            from graph import llm_call
            result = llm_call({"section": mock_section, "completed_sections": []})
            assert isinstance(result["completed_sections"], list)
            assert len(result["completed_sections"]) == 1

    def test_llm_call_content_is_string(self):
        """llm_call completed section content should be a string."""
        mock_response = MagicMock()
        mock_response.content = "## Section\nContent."

        mock_section = MagicMock()
        mock_section.name = "Background"
        mock_section.description = "Historical context"

        with patch("graph.llm") as mock_llm:
            mock_llm.invoke.return_value = mock_response
            from graph import llm_call
            result = llm_call({"section": mock_section, "completed_sections": []})
            assert isinstance(result["completed_sections"][0], str)


class TestAssignWorkersEdge:
    """Tests for the assign_workers conditional edge."""

    def test_assign_workers_returns_send_objects(self):
        """assign_workers should return a list of Send objects."""
        from graph import assign_workers
        from langgraph.constants import Send

        mock_section_1 = MagicMock()
        mock_section_2 = MagicMock()

        state = {
            "topic": "AI",
            "sections": [mock_section_1, mock_section_2],
            "completed_sections": [],
            "final_report": "",
        }

        result = assign_workers(state)
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(r, Send) for r in result)

    def test_assign_workers_empty_sections(self):
        """assign_workers with no sections should return empty list."""
        from graph import assign_workers
        state = {
            "topic": "AI",
            "sections": [],
            "completed_sections": [],
            "final_report": "",
        }
        result = assign_workers(state)
        assert result == []

    def test_assign_workers_count_matches_sections(self):
        """Number of Send objects should match number of sections."""
        from graph import assign_workers
        sections = [MagicMock() for _ in range(5)]
        state = {
            "topic": "AI",
            "sections": sections,
            "completed_sections": [],
            "final_report": "",
        }
        result = assign_workers(state)
        assert len(result) == 5


class TestSynthesizerNode:
    """Tests for the synthesizer node."""

    def test_synthesizer_returns_final_report_key(self):
        """Synthesizer should return dict with 'final_report' key."""
        from graph import synthesizer
        state = {
            "topic": "AI",
            "sections": [],
            "completed_sections": ["## Intro\nContent.", "## Conclusion\nContent."],
            "final_report": "",
        }
        result = synthesizer(state)
        assert "final_report" in result

    def test_synthesizer_joins_sections(self):
        """Synthesizer should join all completed sections."""
        from graph import synthesizer
        state = {
            "topic": "AI",
            "sections": [],
            "completed_sections": ["Section 1 content.", "Section 2 content."],
            "final_report": "",
        }
        result = synthesizer(state)
        assert "Section 1 content." in result["final_report"]
        assert "Section 2 content." in result["final_report"]

    def test_synthesizer_uses_separator(self):
        """Synthesizer should use markdown separator between sections."""
        from graph import synthesizer
        state = {
            "topic": "AI",
            "sections": [],
            "completed_sections": ["Part A", "Part B"],
            "final_report": "",
        }
        result = synthesizer(state)
        assert "---" in result["final_report"]

    def test_synthesizer_empty_sections(self):
        """Synthesizer with empty completed_sections should return empty string."""
        from graph import synthesizer
        state = {
            "topic": "AI",
            "sections": [],
            "completed_sections": [],
            "final_report": "",
        }
        result = synthesizer(state)
        assert result["final_report"] == ""

    def test_synthesizer_single_section(self):
        """Synthesizer with one section should return it as-is."""
        from graph import synthesizer
        state = {
            "topic": "AI",
            "sections": [],
            "completed_sections": ["Only section content."],
            "final_report": "",
        }
        result = synthesizer(state)
        assert "Only section content." in result["final_report"]
