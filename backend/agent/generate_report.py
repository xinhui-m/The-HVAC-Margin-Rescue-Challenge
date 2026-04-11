# backend/agent/generate_report.py

from risk_scoring import rank_projects_by_risk
from root_cause import analyze_root_causes
from recommendations import generate_recommendations


def generate_agent_report(projects: list[dict], top_n: int = 10) -> dict:
    """
    Main entry point for the agent.
    Takes all projects, returns full analysis of the worst ones.
    """
    # Step 1: Score and rank all projects
    ranked = rank_projects_by_risk(projects)
    at_risk = [p for p in ranked if p["is_at_risk"]][:top_n]
    
    # Step 2: Analyze each at-risk project
    analyzed_projects = []
    total_recoverable = 0
    
    for project in at_risk:
        causes = analyze_root_causes(project)
        recs = generate_recommendations(project, causes)
        
        project_recoverable = sum(r["dollar_impact"] or 0 for r in recs)
        total_recoverable += project_recoverable
        
        analyzed_projects.append({
            "project_id": project["project_id"],
            "project_name": project["project_name"],
            "risk_score": project["risk_score"],
            "bid_margin": project.get("bid_margin", 0),
            "realized_margin": project.get("realized_margin", 0),
            "margin_delta": project["margin_delta"],
            "root_causes": causes,
            "recommendations": recs,
            "recoverable_amount": project_recoverable
        })
    
    return {
        "summary": {
            "total_projects_analyzed": len(projects),
            "projects_at_risk": len(at_risk),
            "total_recoverable_amount": total_recoverable
        },
        "projects": analyzed_projects
    }