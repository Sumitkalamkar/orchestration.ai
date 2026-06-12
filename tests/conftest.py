"""
conftest.py — shared fixtures and mocks for all tests.
Mocks out all LLM/LangGraph calls so tests run without API keys.
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient


# ─── Mock data ────────────────────────────────────────────────────────────────

MOCK_SECTIONS = [
    {"name": "Introduction", "description": "Overview of the topic"},
    {"name": "Background",   "description": "Historical context and development"},
    {"name": "Conclusion",   "description": "Summary and future directions"},
]

MOCK_FINAL_REPORT = """## Introduction
Overview content here.

---

## Background
Background content here.

---

## Conclusion
Conclusion content here."""


# ─── Mock Section/Sections Pydantic models ────────────────────────────────────

def make_mock_section(name: str, description: str):
    section = MagicMock()
    section.name = name
    section.description = description
    return section


def make_mock_sections():
    mock_sections_obj = MagicMock()
    mock_sections_obj.sections = [
        make_mock_section(s["name"], s["description"]) for s in MOCK_SECTIONS
    ]
    return mock_sections_obj


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def mock_graph_state():
    """Returns a fake LangGraph final state."""
    return {
        "topic": "Artificial Intelligence",
        "sections": [make_mock_section(s["name"], s["description"]) for s in MOCK_SECTIONS],
        "completed_sections": [f"## {s['name']}\nContent." for s in MOCK_SECTIONS],
        "final_report": MOCK_FINAL_REPORT,
    }


@pytest.fixture(scope="session")
def mock_planner_output():
    """Returns a fake planner structured output."""
    return make_mock_sections()


@pytest.fixture(scope="session")
def client(mock_graph_state, mock_planner_output):
    """
    TestClient with all LLM calls patched out.
    No real API calls are made during tests.
    """
    with patch("graph.ChatGroq") as mock_llm_cls, \
         patch("graph.orchestrator_worker") as mock_graph, \
         patch("graph.planner") as mock_planner:

        # Patch planner (plan-sections endpoint)
        mock_planner.invoke.return_value = mock_planner_output

        # Patch full graph (generate-report endpoint)
        mock_graph.invoke.return_value = mock_graph_state

        # Patch raw LLM (llm_call node)
        mock_llm_instance = MagicMock()
        mock_llm_instance.invoke.return_value = MagicMock(content="## Section\nContent.")
        mock_llm_instance.with_structured_output.return_value = mock_planner
        mock_llm_cls.return_value = mock_llm_instance

        from backend import app
        with TestClient(app) as c:
            yield c
