def calculate_risk_score(project: dict) -> dict:
    """
    Input: single project with aggregated metrics
    Output: project with:
      - risk_score (0-100)
      - is_at_risk flag
      - margin_delta
      - severity label
    """

    bid_margin = float(project.get("bid_margin", 0) or 0)
    realized_margin = float(project.get("realized_margin", 0) or 0)
    margin_delta = bid_margin - realized_margin

    max_billing_gap = float(project.get("max_billing_gap", 0) or 0)
    total_co_amount = float(project.get("total_co_amount", 0) or 0)
    total_retention_held = float(project.get("total_retention_held", 0) or 0)
    max_labor_overrun_ratio = float(project.get("max_labor_overrun_ratio", 0) or 0)
    max_material_overrun_ratio = float(project.get("max_material_overrun_ratio", 0) or 0)
    rfi_count = int(project.get("rfi_count", 0) or 0)
    flagged_sov_count = int(project.get("flagged_sov_count", 0) or 0)

    risk_score = 0

    # 1. Margin erosion is the strongest signal
    if margin_delta >= 0.75:
        risk_score += 35
    elif margin_delta >= 0.40:
        risk_score += 28
    elif margin_delta >= 0.20:
        risk_score += 20
    elif margin_delta >= 0.10:
        risk_score += 12
    elif margin_delta >= 0.05:
        risk_score += 6

    # 2. Negative realized margin is a major red flag
    if realized_margin <= -0.50:
        risk_score += 30
    elif realized_margin <= -0.20:
        risk_score += 24
    elif realized_margin < 0:
        risk_score += 16

    # 3. Billing lag
    if max_billing_gap >= 0.20:
        risk_score += 12
    elif max_billing_gap >= 0.10:
        risk_score += 8
    elif max_billing_gap >= 0.05:
        risk_score += 4

    # 4. Labor overrun severity
    if max_labor_overrun_ratio >= 2.0:
        risk_score += 10
    elif max_labor_overrun_ratio >= 1.5:
        risk_score += 7
    elif max_labor_overrun_ratio >= 1.0:
        risk_score += 4

    # 5. Material overrun severity
    if max_material_overrun_ratio >= 2.0:
        risk_score += 10
    elif max_material_overrun_ratio >= 1.5:
        risk_score += 7
    elif max_material_overrun_ratio >= 1.0:
        risk_score += 4

    # 6. Large change-order exposure
    if total_co_amount >= 500000:
        risk_score += 8
    elif total_co_amount >= 200000:
        risk_score += 5
    elif total_co_amount >= 100000:
        risk_score += 3

    # 7. Retention held
    if total_retention_held >= 500000:
        risk_score += 6
    elif total_retention_held >= 250000:
        risk_score += 4
    elif total_retention_held > 0:
        risk_score += 2

    # 8. Complexity / coordination pressure
    if rfi_count >= 60:
        risk_score += 6
    elif rfi_count >= 40:
        risk_score += 4
    elif rfi_count >= 20:
        risk_score += 2

    # 9. Erosion spread across many scopes
    if flagged_sov_count >= 12:
        risk_score += 6
    elif flagged_sov_count >= 8:
        risk_score += 4
    elif flagged_sov_count >= 4:
        risk_score += 2

    risk_score = min(risk_score, 100)

    # Severity label for frontend if you want it
    if realized_margin < 0 or risk_score >= 70:
        severity = "critical"
    elif risk_score >= 40:
        severity = "warning"
    else:
        severity = "watch"

    is_at_risk = (
        margin_delta >= 0.05
        or realized_margin < 0
        or max_billing_gap >= 0.05
        or max_labor_overrun_ratio >= 1.0
        or max_material_overrun_ratio >= 1.0
    )

    return {
        **project,
        "risk_score": risk_score,
        "is_at_risk": is_at_risk,
        "margin_delta": margin_delta,
        "severity": severity,
    }


def rank_projects_by_risk(projects: list[dict]) -> list[dict]:
    """
    Return projects sorted by risk, using tie-breakers so
    projects do not all bunch up with the same score.
    """
    scored = [calculate_risk_score(p) for p in projects]

    return sorted(
        scored,
        key=lambda p: (
            p.get("risk_score", 0),
            -(p.get("realized_margin", 0) or 0),   # more negative margin = worse
            p.get("margin_delta", 0),
            p.get("recoverable_amount", 0) or 0,
            p.get("total_co_amount", 0) or 0,
        ),
        reverse=True,
    )