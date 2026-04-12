def generate_recommendations(project: dict, causes: list[dict]) -> list[dict]:
    recommendations = []

    cause_types = {c["type"] for c in causes}

    if "billing_lag" in cause_types:
        recommendations.append({
            "action": "Submit pay application for completed but underbilled work.",
            "priority": "high",
            "dollar_impact": round(project["max_billing_gap"] * project["total_co_amount"], 2) if project["total_co_amount"] else None,
        })

    if "retention_exposure" in cause_types:
        recommendations.append({
            "action": "Push for retention release as closeout approaches.",
            "priority": "high",
            "dollar_impact": round(project["total_retention_held"], 2),
        })

    if "change_order_opportunity" in cause_types:
        recommendations.append({
            "action": "Audit approved and pending change orders for immediate billing and recovery.",
            "priority": "high",
            "dollar_impact": round(project["total_co_amount"], 2),
        })

    if "material_overrun" in cause_types:
        recommendations.append({
            "action": "Review buyout, substitutions, and late-stage procurement on flagged SOV lines.",
            "priority": "medium",
            "dollar_impact": None,
        })

    if "labor_overrun" in cause_types:
        recommendations.append({
            "action": "Audit labor loading and overtime concentration on flagged scopes.",
            "priority": "medium",
            "dollar_impact": None,
        })

    return recommendations