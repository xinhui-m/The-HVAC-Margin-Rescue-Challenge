def generate_recommendations(project: dict, causes: list[dict]) -> list[dict]:
    """
    Generate targeted recommendations with estimated dollar impact.
    """

    recommendations = []
    cause_types = {c["type"] for c in causes}

    billing_gap = float(project.get("max_billing_gap", 0) or 0)
    retention_held = float(project.get("total_retention_held", 0) or 0)
    total_co_amount = float(project.get("total_co_amount", 0) or 0)
    labor_ratio = float(project.get("max_labor_overrun_ratio", 0) or 0)
    material_ratio = float(project.get("max_material_overrun_ratio", 0) or 0)
    rfi_count = int(project.get("rfi_count", 0) or 0)

    # Useful optional fields if available
    contract_value = float(
        project.get("contract_value", 0)
        or project.get("contract_amount", 0)
        or 0
    )

    actual_labor_cost = float(project.get("actual_labor_cost", 0) or 0)
    actual_material_cost = float(project.get("actual_material_cost", 0) or 0)

    # 1. Billing lag
    if "billing_lag" in cause_types:
        billing_recovery = billing_gap * contract_value if contract_value > 0 else 0

        recommendations.append({
            "action": f"Submit or accelerate the next pay application to close the estimated {(billing_gap * 100):.1f}% billing gap on completed work.",
            "priority": "high",
            "dollar_impact": round(billing_recovery, 2) if billing_recovery > 0 else None
        })

    # 2. Retention exposure
    if "retention_exposure" in cause_types and retention_held > 0:
        recommendations.append({
            "action": f"Push for retention release and closeout documentation to unlock approximately ${retention_held:,.0f} in held cash.",
            "priority": "high",
            "dollar_impact": round(retention_held, 2)
        })

    # 3. Change orders
    if "change_order_opportunity" in cause_types and total_co_amount > 0:
        recommendations.append({
            "action": f"Audit approved and pending change orders and convert up to ${total_co_amount:,.0f} into billable recovery where support exists.",
            "priority": "high",
            "dollar_impact": round(total_co_amount, 2)
        })

    # 4. Material overrun
    if "material_overrun" in cause_types:
        # Conservative estimate: maybe recover 10% of actual material spend
        # or use contract-based fallback if actual material cost is unavailable
        if actual_material_cost > 0:
            material_recovery = actual_material_cost * 0.10
        elif contract_value > 0:
            material_recovery = contract_value * 0.03
        else:
            material_recovery = 0

        recommendations.append({
            "action": f"Review buyout, substitutions, vendor pricing, and late-stage procurement on scopes showing up to {material_ratio:.1f}x material overrun.",
            "priority": "medium",
            "dollar_impact": round(material_recovery, 2) if material_recovery > 0 else None
        })

    # 5. Labor overrun
    if "labor_overrun" in cause_types:
        # Conservative estimate: maybe recover 8% of actual labor spend
        # or use contract-based fallback if actual labor cost is unavailable
        if actual_labor_cost > 0:
            labor_recovery = actual_labor_cost * 0.08
        elif contract_value > 0:
            labor_recovery = contract_value * 0.025
        else:
            labor_recovery = 0

        recommendations.append({
            "action": f"Audit labor loading, overtime concentration, and crew mix on scopes showing up to {labor_ratio:.1f}x labor overrun.",
            "priority": "medium",
            "dollar_impact": round(labor_recovery, 2) if labor_recovery > 0 else None
        })

    # 6. High RFI complexity
    if "high_rfi_complexity" in cause_types:
        # Small recovery estimate tied to coordination cleanup
        if contract_value > 0:
            rfi_recovery = min(contract_value * 0.01, 50000)
        else:
            rfi_recovery = min(rfi_count * 500, 50000)

        recommendations.append({
            "action": f"Review the {rfi_count} RFIs for repeated coordination issues and identify scope changes or rework that should be documented for recovery.",
            "priority": "medium",
            "dollar_impact": round(rfi_recovery, 2) if rfi_recovery > 0 else None
        })

    # 7. Multi-scope erosion
    if "multi_scope_erosion" in cause_types:
        if contract_value > 0:
            scope_recovery = contract_value * 0.015
        else:
            scope_recovery = 0

        recommendations.append({
            "action": "Escalate this project for PM review because erosion is spread across multiple scopes rather than one isolated line item.",
            "priority": "medium",
            "dollar_impact": round(scope_recovery, 2) if scope_recovery > 0 else None
        })

    return recommendations[:5]