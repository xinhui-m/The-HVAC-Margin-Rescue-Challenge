from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add backend/agent to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "agent"))

from generate_report import (
    build_project_summaries_from_flagged_csv,
    generate_agent_report,
)
from risk_scoring import rank_projects_by_risk, calculate_risk_score
from root_cause import analyze_root_causes
from recommendations import generate_recommendations

app = FastAPI(title="HVAC Margin Rescue Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Build an absolute path so it works no matter where you run the server from
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FLAGGED_CSV_PATH = os.path.join(BASE_DIR, "data", "final_data", "projects_flagged.csv")


@app.get("/")
def health_check():
    return {"status": "ok", "message": "HVAC Margin Rescue Agent API"}


@app.get("/api/analyze")
def analyze_projects():
    """
    Main endpoint - runs the agent on real aggregated data
    and returns the full report.
    """
    projects = build_project_summaries_from_flagged_csv(FLAGGED_CSV_PATH)
    report = generate_agent_report(projects, top_n=5)
    return report


@app.get("/api/projects")
def get_all_projects():
    """
    Returns all summarized projects with risk scores.
    """
    projects = build_project_summaries_from_flagged_csv(FLAGGED_CSV_PATH)
    ranked = rank_projects_by_risk(projects)
    return {"projects": ranked}


@app.get("/api/project/{project_id}")
def get_project_detail(project_id: str):
    """
    Returns detailed analysis for a single project.
    """
    projects = build_project_summaries_from_flagged_csv(FLAGGED_CSV_PATH)
    project = next((p for p in projects if p["project_id"] == project_id), None)

    if not project:
        return {"error": "Project not found"}

    scored = calculate_risk_score(project)
    causes = analyze_root_causes(scored)
    recs = generate_recommendations(scored, causes)

    return {
        **scored,
        "root_causes": causes,
        "recommendations": recs,
        "recoverable_amount": sum(r.get("dollar_impact") or 0 for r in recs),
    }