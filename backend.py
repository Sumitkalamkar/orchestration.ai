"""
FastAPI backend — imports the graph from graph.py (same module used by LangGraph Studio).
Run with: uvicorn backend:app --reload --port 8000
"""

from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

from graph import HumanMessage, SystemMessage, orchestrator_worker, planner

app = FastAPI(title="OrchestrAI Report Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Request / Response models ────────────────────────────────────────────────

class TopicRequest(BaseModel):
    """Request model for report generation endpoints."""

    topic: str

    @field_validator("topic")
    @classmethod
    def topic_must_not_be_empty(cls, v):
        """Validate that topic is not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError("topic must not be empty")
        return v


class SectionOut(BaseModel):
    """Output model for a single report section."""

    name: str
    description: str


class PlanResponse(BaseModel):
    """Response model for the plan-sections endpoint."""

    sections: List[SectionOut]


class ReportResponse(BaseModel):
    """Response model for the generate-report endpoint."""

    topic: str
    sections: List[SectionOut]
    final_report: str


# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/plan-sections", response_model=PlanResponse)
def plan_sections(req: TopicRequest):
    """Returns the planned section structure without writing content."""
    try:
        result = planner.invoke([
            SystemMessage(content="Generate a plan for the report."),
            HumanMessage(content=f"Here is the report topic: {req.topic}"),
        ])
        return PlanResponse(
            sections=[
                SectionOut(name=s.name, description=s.description)
                for s in result.sections
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/generate-report", response_model=ReportResponse)
def generate_report(req: TopicRequest):
    """Runs the full LangGraph graph and returns the complete report."""
    try:
        state = orchestrator_worker.invoke({"topic": req.topic})
        return ReportResponse(
            topic=req.topic,
            sections=[
                SectionOut(name=s.name, description=s.description)
                for s in state["sections"]
            ],
            final_report=state["final_report"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
