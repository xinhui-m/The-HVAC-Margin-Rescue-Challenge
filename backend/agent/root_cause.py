def analyze_root_causes(project: dict) -> list[dict]:
    """
    Return the most important project-specific root causes,
    ranked by severity instead of listing every possible issue.
    """
    causes = []

    labor_ratio = float(project.get("max_labor_overrun_ratio", 0) or 0)
    material_ratio = float(project.get("max_material_overrun_ratio", 0) or 0)
    billing_gap = float(project.get("max_billing_gap", 0) or 0)
    retention_flags = int(project.get("retention_flag_count", 0) or 0)
    closeout_flags = int(project.get("closeout_flag_count", 0) or 0)
    total_co_amount = float(project.get("total_co_amount", 0) or 0)
    rfi_count = int(project.get("rfi_count", 0) or 0)
    flagged_sov_count = int(project.get("flagged_sov_count", 0) or 0)

    scored_causes = []

    # Material overrun
    if material_ratio >= 1.5:
        scored_causes.append({
            "type": "material_overrun",
            "score": 95,
            "explanation": f"Material costs are severely over estimate, peaking at about {material_ratio:.1f}x across flagged work scopes."
        })
    elif material_ratio >= 1.0:
        scored_causes.append({
            "type": "material_overrun",
            "score": 75,
            "explanation": f"Material spending is above estimate, reaching roughly {material_ratio:.1f}x on flagged scopes."
        })

    # Labor overrun
    if labor_ratio >= 1.5:
        scored_causes.append({
            "type": "labor_overrun",
            "score": 90,
            "explanation": f"Labor costs are severely above estimate, reaching about {labor_ratio:.1f}x on flagged work scopes."
        })
    elif labor_ratio >= 0.75:
        scored_causes.append({
            "type": "labor_overrun",
            "score": 70,
            "explanation": f"Labor costs are trending above estimate, with overruns concentrated in flagged scopes."
        })

    # Billing lag
    if billing_gap >= 0.15:
        scored_causes.append({
            "type": "billing_lag",
            "score": 85,
            "explanation": f"Billing is materially behind progress, with an estimated gap of {(billing_gap * 100):.1f}%."
        })
    elif billing_gap >= 0.05:
        scored_causes.append({
            "type": "billing_lag",
            "score": 65,
            "explanation": f"Completed work appears underbilled, leaving a moderate billing gap of {(billing_gap * 100):.1f}%."
        })

    # Retention / closeout
    if retention_flags > 0 and closeout_flags > 0:
        scored_causes.append({
            "type": "retention_exposure",
            "score": 80,
            "explanation": "The project appears to be nearing closeout while retention is still being held, limiting cash recovery."
        })
    elif retention_flags > 0:
        scored_causes.append({
            "type": "retention_exposure",
            "score": 60,
            "explanation": "Retention is still being held, which may delay cash recovery."
        })

    # Change orders
    if total_co_amount >= 300000:
        scored_causes.append({
            "type": "change_order_opportunity",
            "score": 78,
            "explanation": f"The project has meaningful change-order exposure (${total_co_amount:,.0f}) that may represent immediate recovery opportunity."
        })
    elif total_co_amount >= 100000:
        scored_causes.append({
            "type": "change_order_opportunity",
            "score": 58,
            "explanation": f"There is change-order value (${total_co_amount:,.0f}) that could support recovery if billed promptly."
        })

    # High complexity
    if rfi_count >= 60:
        scored_causes.append({
            "type": "high_rfi_complexity",
            "score": 72,
            "explanation": f"High RFI volume ({rfi_count}) suggests coordination friction, scope churn, or execution complexity."
        })
    elif rfi_count >= 40:
        scored_causes.append({
            "type": "high_rfi_complexity",
            "score": 55,
            "explanation": f"Elevated RFI volume ({rfi_count}) points to above-normal coordination complexity."
        })

    # Concentrated flagged scope
    if flagged_sov_count >= 10:
        scored_causes.append({
            "type": "multi_scope_erosion",
            "score": 68,
            "explanation": f"Margin erosion is spread across {flagged_sov_count} flagged SOV lines rather than isolated to one scope."
        })

    # Sort by severity and keep only top 3-4
    scored_causes.sort(key=lambda c: c["score"], reverse=True)

    return [
        {
            "type": cause["type"],
            "explanation": cause["explanation"]
        }
        for cause in scored_causes[:4]
    ]