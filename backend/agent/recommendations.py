# backend/agent/recommendations.py

def generate_recommendations(project: dict, root_causes: list[dict]) -> list[dict]:
    """
    Takes a project and its root causes, returns specific actionable recommendations.
    """
    recommendations = []
    
    for cause in root_causes:
        if cause["category"] == "billing":
            recommendations.append({
                "action": "SUBMIT_INVOICE",
                "priority": "high",
                "dollar_impact": cause["gap_dollars"],
                "description": f"Submit invoice for ${cause['gap_dollars']:,.0f} in unbilled work",
                "details": "Review completed work orders and submit billing for all finished milestones"
            })
        
        elif cause["category"] == "labor":
            recommendations.append({
                "action": "SUBMIT_CHANGE_ORDER",
                "priority": "high" if cause["severity"] == "high" else "medium",
                "dollar_impact": cause["overrun_dollars"],
                "description": f"Submit change order for ${cause['overrun_dollars']:,.0f} in labor overruns",
                "details": "Document scope changes or site conditions that drove additional labor hours"
            })
        
        elif cause["category"] == "material":
            recommendations.append({
                "action": "SUBMIT_CHANGE_ORDER",
                "priority": "high" if cause["severity"] == "high" else "medium",
                "dollar_impact": cause["overrun_dollars"],
                "description": f"Submit change order for ${cause['overrun_dollars']:,.0f} in material cost increases",
                "details": "Document material substitutions, price escalations, or specification changes"
            })
    
    # Sort: high priority first, then by dollar impact
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda x: (priority_order[x["priority"]], -(x["dollar_impact"] or 0)))
    
    return recommendations
