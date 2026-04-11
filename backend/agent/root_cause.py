# root_cause.py

def analyze_root_causes(project: dict) -> list[dict]:
    """
    Input: Project with cost breakdowns
    Output: List of root causes with severity and explanation
    """
    causes = []
    
    # Labor overrun
    labor_budget = project.get("labor_budget", 0)
    labor_actual = project.get("labor_actual", 0)
    if labor_budget > 0:
        labor_overrun = (labor_actual - labor_budget) / labor_budget
        if labor_overrun > 0.1:  # 10% over
            causes.append({
                "category": "labor",
                "severity": "high" if labor_overrun > 0.25 else "medium",
                "overrun_pct": round(labor_overrun * 100, 1),
                "overrun_dollars": labor_actual - labor_budget,
                "explanation": f"Labor costs exceeded budget by {round(labor_overrun * 100)}% (${labor_actual - labor_budget:,.0f})"
            })
    
    # Material overrun
    material_budget = project.get("material_budget", 0)
    material_actual = project.get("material_actual", 0)
    if material_budget > 0:
        material_overrun = (material_actual - material_budget) / material_budget
        if material_overrun > 0.1:
            causes.append({
                "category": "material",
                "severity": "high" if material_overrun > 0.25 else "medium",
                "overrun_pct": round(material_overrun * 100, 1),
                "overrun_dollars": material_actual - material_budget,
                "explanation": f"Material costs exceeded budget by {round(material_overrun * 100)}% (${material_actual - material_budget:,.0f})"
            })
    
    # Billing gap
    billing_gap = project.get("billing_gap", 0)
    if billing_gap > 10000:
        causes.append({
            "category": "billing",
            "severity": "high" if billing_gap > 50000 else "medium",
            "gap_dollars": billing_gap,
            "explanation": f"Unbilled costs of ${billing_gap:,.0f} not yet invoiced"
        })
    
    return causes