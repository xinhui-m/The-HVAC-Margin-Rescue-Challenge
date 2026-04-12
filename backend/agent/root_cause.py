def analyze_root_causes(project: dict) -> list[dict]:
    causes = []

    if project["max_material_overrun_ratio"] >= 1.0:
        causes.append({
            "type": "material_overrun",
            "explanation": "Material spending is significantly above estimate across flagged SOV lines."
        })

    if project["max_labor_overrun_ratio"] >= 0.5:
        causes.append({
            "type": "labor_overrun",
            "explanation": "Labor costs are trending above estimate on flagged work scopes."
        })

    if project["underbilling_count"] > 0 or project["max_billing_gap"] > 0.05:
        causes.append({
            "type": "billing_lag",
            "explanation": "Completed work appears underbilled, creating a billing gap."
        })

    if project["retention_flag_count"] > 0 and project["pct_complete"] >= 95:
        causes.append({
            "type": "retention_exposure",
            "explanation": "Project is near completion but retention is still being held."
        })

    if project["total_co_amount"] > 0:
        causes.append({
            "type": "change_order_opportunity",
            "explanation": "There is change-order value that may represent recovery opportunity."
        })

    if project["rfi_count"] >= 40:
        causes.append({
            "type": "high_rfi_complexity",
            "explanation": "High RFI volume suggests scope complexity or coordination friction."
        })

    return causes