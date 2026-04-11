# backend/agent/test_agent.py

from risk_scoring import rank_projects_by_risk
from root_cause import analyze_root_causes
from recommendations import generate_recommendations
from generate_report import generate_agent_report
import json
# from root_cause import analyze_root_causes  # Comment this out for now

mock_projects = [
    {
        "project_id": "P-001",
        "project_name": "Downtown Office HVAC",
        "bid_margin": 0.15,
        "realized_margin": 0.02,
        "labor_budget": 200000,
        "labor_actual": 280000,
        "material_budget": 100000,
        "material_actual": 105000,
        "billing_gap": 45000
    },
    {
        "project_id": "P-002", 
        "project_name": "Hospital Wing B",
        "bid_margin": 0.12,
        "realized_margin": 0.10,
        "labor_budget": 150000,
        "labor_actual": 155000,
        "material_budget": 80000,
        "material_actual": 82000,
        "billing_gap": 5000
    },
    {
        "project_id": "P-003",
        "project_name": "Retail Center Phase 2",
        "bid_margin": 0.18,
        "realized_margin": -0.05,
        "labor_budget": 300000,
        "labor_actual": 450000,
        "material_budget": 200000,
        "material_actual": 260000,
        "billing_gap": 120000
    }
]

# Test risk scoring only
ranked = rank_projects_by_risk(mock_projects)
print("=== RISK RANKING ===")
for p in ranked:
    print(f"{p['project_name']}: Score {p['risk_score']}, At Risk: {p['is_at_risk']}")

ranked = rank_projects_by_risk(mock_projects)
worst = ranked[0]
causes = analyze_root_causes(worst)
recs = generate_recommendations(worst, causes)

print("\n=== RECOMMENDATIONS ===")
for rec in recs:
    print(f"[{rec['priority'].upper()}] {rec['description']}")

# Run the full agent
report = generate_agent_report(mock_projects)

# Pretty print the result
print(json.dumps(report, indent=2))