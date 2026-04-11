# risk_scoring.py

def calculate_risk_score(project: dict) -> dict:
    """
    Input: Single project with aggregated metrics
    Output: Project with risk_score (0-100) and is_at_risk flag
    """
    bid_margin = project.get("bid_margin", 0)
    realized_margin = project.get("realized_margin", 0)
    margin_delta = bid_margin - realized_margin
    
    # Core risk: margin erosion
    risk_score = 0
    
    # Margin delta is the primary signal
    if margin_delta > 0.15:
        risk_score += 50
    elif margin_delta > 10:
        risk_score += 35
    elif margin_delta > 0.05:
        risk_score += 20
    
    # Billing gap adds risk
    billing_gap = project.get("billing_gap", 0)
    if billing_gap > 50000:
        risk_score += 25
    elif billing_gap > 20000:
        risk_score += 15
    
    # Negative realized margin is critical
    if realized_margin < 0:
        risk_score += 25
    
    return {
        **project,
        "risk_score": min(risk_score, 100),
        "is_at_risk": margin_delta > 0.05 or realized_margin < 0,
        "margin_delta": margin_delta
    }


def rank_projects_by_risk(projects: list[dict]) -> list[dict]:
    """Return projects sorted by risk, highest first"""
    scored = [calculate_risk_score(p) for p in projects]
    return sorted(scored, key=lambda x: x["risk_score"], reverse=True)