# backend/api/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

# Add parent directory to path so we can import agent modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agent'))

from generate_report import generate_agent_report

app = FastAPI(title="HVAC Margin Rescue Agent API")

# Allow frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data for now - replace with real data from aggregation team
MOCK_PROJECTS = [
    {
        "project_id": "P-001",
        "project_name": "Downtown Office HVAC",
        "bid_margin": 0.15,
        "realized_margin": 0.02,
        "labor_budget": 200000,
        "labor_actual": 280000,
        "material_budget": 100000,
        "material_actual": 105000,
        "billing_gap": 45000
    },
    {
        "project_id": "P-002",
        "project_name": "Hospital Wing B",
        "bid_margin": 0.12,
        "realized_margin": 0.10,
        "labor_budget": 150000,
        "labor_actual": 155000,
        "material_budget": 80000,
        "material_actual": 82000,
        "billing_gap": 5000
    },
    {
        "project_id": "P-003",
        "project_name": "Retail Center Phase 2",
        "bid_margin": 0.18,
        "realized_margin": -0.05,
        "labor_budget": 300000,
        "labor_actual": 450000,
        "material_budget": 200000,
        "material_actual": 260000,
        "billing_gap": 120000
    }
]


@app.get("/")
def health_check():
    return {"status": "ok", "message": "HVAC Margin Rescue Agent API"}


@app.get("/api/analyze")
def analyze_projects():
    """
    Main endpoint - runs the agent and returns the full report.
    """
    report = generate_agent_report(MOCK_PROJECTS)
    return report


@app.get("/api/projects")
def get_all_projects():
    """
    Returns all projects with their risk scores (without full analysis).
    """
    from risk_scoring import rank_projects_by_risk
    return {"projects": rank_projects_by_risk(MOCK_PROJECTS)}


@app.get("/api/project/{project_id}")
def get_project_detail(project_id: str):
    """
    Returns detailed analysis for a single project.
    """
    from risk_scoring import calculate_risk_score
    from root_cause import analyze_root_causes
    from recommendations import generate_recommendations
    
    project = next((p for p in MOCK_PROJECTS if p["project_id"] == project_id), None)
    
    if not project:
        return {"error": "Project not found"}
    
    scored = calculate_risk_score(project)
    causes = analyze_root_causes(scored)
    recs = generate_recommendations(scored, causes)
    
    return {
        **scored,
        "root_causes": causes,
        "recommendations": recs,
        "recoverable_amount": sum(r["dollar_impact"] or 0 for r in recs)
    }