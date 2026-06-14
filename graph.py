"""
graph.py — LangGraph orchestrator-worker graph.
Imported by langgraph.json for LangGraph Studio,
and also used by backend.py for the FastAPI server.
"""

import os
import operator
from typing import Annotated, List
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# ─── LLM ──────────────────────────────────────────────────────────────────────

llm = ChatGroq(model="llama-3.3-70b-versatile")

# ─── Schemas ──────────────────────────────────────────────────────────────────

class Section(BaseModel):
    name: str = Field(description="Name for this section of the report")
    description: str = Field(
        description="Brief overview of the main topics and concepts of the section"
    )

class Sections(BaseModel):
    sections: List[Section] = Field(description="Sections of the report")

planner = llm.with_structured_output(Sections)

# ─── State ────────────────────────────────────────────────────────────────────

class State(TypedDict):
    topic: str
    sections: list
    completed_sections: Annotated[list, operator.add]
    final_report: str

class WorkerState(TypedDict):
    section: Section
    completed_sections: Annotated[list, operator.add]

# ─── Nodes ────────────────────────────────────────────────────────────────────

def orchestrator(state: State):
    """Orchestrator that generates a plan for the report."""
    report_sections = planner.invoke([
        SystemMessage(content="Generate a plan for the report."),
        HumanMessage(content=f"Here is the report topic: {state['topic']}"),
    ])
    return {"sections": report_sections.sections}

def llm_call(state: WorkerState):
    """Worker that writes a single section of the report."""
    section = llm.invoke([
        SystemMessage(
            content="Write a report section following the provided name and description. "
                    "Include no preamble for each section. Use markdown formatting."
        ),
        HumanMessage(
            content=f"Here is the section name: {state['section'].name} "
                    f"and description: {state['section'].description}"
        ),
    ])
    return {"completed_sections": [section.content]}

def assign_workers(state: State):
    """Conditional edge — fans out one worker per section."""
    return [Send("llm_call", {"section": s}) for s in state["sections"]]

def synthesizer(state: State):
    """Synthesizes all completed sections into the final report."""
    completed_report_sections = "\n\n---\n\n".join(state["completed_sections"])
    return {"final_report": completed_report_sections}

# ─── Graph ────────────────────────────────────────────────────────────────────

builder = StateGraph(State)
builder.add_node("orchestrator", orchestrator)
builder.add_node("llm_call", llm_call)
builder.add_node("synthesizer", synthesizer)
builder.add_edge(START, "orchestrator")
builder.add_conditional_edges("orchestrator", assign_workers, ["llm_call"])
builder.add_edge("llm_call", "synthesizer")
builder.add_edge("synthesizer", END)

orchestrator_worker = builder.compile()
