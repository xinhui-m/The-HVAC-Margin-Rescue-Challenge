# backend/agent/generate_report.py

from __future__ import annotations

import pandas as pd
from collections import Counter

from risk_scoring import rank_projects_by_risk
from root_cause import analyze_root_causes
from recommendations import generate_recommendations


def build_project_summaries_from_flagged_csv(csv_path: str) -> list[dict]:
    """
    Reads projects_flagged.csv and collapses flagged SOV rows
    into one project-level summary dict per project.
    """
    df = pd.read_csv(csv_path)

    project_summaries = []

    for project_id, group in df.groupby("project_id"):
        first = group.iloc[0]

        flag_reasons = []
        for reason_str in group["flag_reason"].dropna():
            parts = [r.strip() for r in str(reason_str).split(",") if r.strip()]
            flag_reasons.extend(parts)

        reason_counts = Counter(flag_reasons)

        summary = {
            "project_id": project_id,
            "project_name": first["project_name"],
            "gc_name": first.get("gc_name"),
            "risk_score": float(group["risk_score"].max()),
            "is_at_risk": True,

            "bid_margin": float(first.get("bid_margin", 0) or 0),
            "realized_margin": float(first.get("realized_margin", 0) or 0),
            "margin_delta": float(first.get("bid_margin", 0) or 0) - float(first.get("realized_margin", 0) or 0),

            "flagged_sov_count": int(len(group)),
            "top_flag_reasons": [reason for reason, _ in reason_counts.most_common(5)],

            "avg_labor_overrun_ratio": float(group["labor_overrun_ratio"].fillna(0).mean()),
            "max_labor_overrun_ratio": float(group["labor_overrun_ratio"].fillna(0).max()),

            "avg_material_overrun_ratio": float(group["material_overrun_ratio"].fillna(0).mean()),
            "max_material_overrun_ratio": float(group["material_overrun_ratio"].fillna(0).max()),

            "avg_billing_gap": float(group["billing_gap"].fillna(0).mean()),
            "max_billing_gap": float(group["billing_gap"].fillna(0).max()),

            "underbilling_count": int(group["underbilling_flag"].fillna(False).sum()),
            "overbilling_count": int(group["overbilling_flag"].fillna(False).sum()),
            "retention_flag_count": int(group["retention_flag"].fillna(False).sum()),
            "closeout_flag_count": int(group["closeout_flag"].fillna(False).sum()),
            "true_closeout_issue_count": int(group["true_closeout_issue"].fillna(False).sum()),

            "total_retention_held": float(group["retention_held"].fillna(0).max()),
            "total_co_amount": float(group["total_co_amount"].fillna(0).max()),
            "rfi_count": int(group["rfi_count"].fillna(0).max()),

            "pct_complete": float(group["pct_complete"].fillna(0).mean()),
            "pct_billed": float(group["pct_billed"].fillna(0).mean()),

            # helpful raw context for later
            "flagged_sov_lines": group["sov_line_id"].dropna().tolist(),
            "key_assumptions_sample": group["key_assumptions"].dropna().head(3).tolist(),
        }

        project_summaries.append(summary)

    return project_summaries


def generate_agent_report(projects: list[dict], top_n: int = 10) -> dict:
    """
    Takes project-level summaries and returns analysis of the worst projects.
    """
    ranked = rank_projects_by_risk(projects)
    at_risk = [p for p in ranked if p.get("is_at_risk", False)][:top_n]

    analyzed_projects = []
    total_recoverable = 0

    for project in at_risk:
        causes = analyze_root_causes(project)
        recs = generate_recommendations(project, causes)

        project_recoverable = sum(r.get("dollar_impact") or 0 for r in recs)
        total_recoverable += project_recoverable

        analyzed_projects.append({
            "project_id": project["project_id"],
            "project_name": project["project_name"],
            "gc_name": project.get("gc_name"),
            "risk_score": project["risk_score"],
            "bid_margin": project.get("bid_margin", 0),
            "realized_margin": project.get("realized_margin", 0),
            "margin_delta": project.get("margin_delta", 0),
            "flagged_sov_count": project.get("flagged_sov_count", 0),
            "top_flag_reasons": project.get("top_flag_reasons", []),
            "root_causes": causes,
            "recommendations": recs,
            "recoverable_amount": project_recoverable,
        })

    return {
        "summary": {
            "total_projects_analyzed": len(projects),
            "projects_at_risk": len(at_risk),
            "total_recoverable_amount": total_recoverable,
        },
        "projects": analyzed_projects,
    }


if __name__ == "__main__":
    projects = build_project_summaries_from_flagged_csv("data/final_data/projects_flagged.csv")
    report = generate_agent_report(projects, top_n=5)
    import json
    print(json.dumps(report, indent=2))