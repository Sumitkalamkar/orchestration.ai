"""
FastAPI backend — imports the graph from graph.py (same module used by LangGraph Studio).
Run with: uvicorn backend:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# Import the compiled graph and shared types from graph.py
from graph import orchestrator_worker, planner, Section, SystemMessage, HumanMessage

app = FastAPI(title="OrchestrAI Report Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Request / Response models ────────────────────────────────────────────────

class TopicRequest(BaseModel):
    topic: str

class SectionOut(BaseModel):
    name: str
    description: str

class PlanResponse(BaseModel):
    sections: List[SectionOut]

class ReportResponse(BaseModel):
    topic: str
    sections: List[SectionOut]
    final_report: str

# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
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
            sections=[SectionOut(name=s.name, description=s.description) for s in result.sections]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-report", response_model=ReportResponse)
def generate_report(req: TopicRequest):
    """Runs the full LangGraph graph and returns the complete report."""
    try:
        state = orchestrator_worker.invoke({"topic": req.topic})
        return ReportResponse(
            topic=req.topic,
            sections=[SectionOut(name=s.name, description=s.description) for s in state["sections"]],
            final_report=state["final_report"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
