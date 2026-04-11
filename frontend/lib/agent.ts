import type { AgentReport, RootCause, Recommendation, Project } from "./types"

// Raw project data type (from aggregation team)
interface RawProject {
  project_id: string
  project_name: string
  contract_amount: number
  actual_cost: number
  billed_amount: number
  bid_margin: number
  realized_margin: number
  labor_budget: number
  labor_actual: number
  material_budget: number
  material_actual: number
  equipment_budget?: number
  equipment_actual?: number
  billing_gap: number
  change_orders_count?: number
  retention_held?: number
}

// Mock data - replace with real data from aggregation team
const MOCK_PROJECTS: RawProject[] = [
  {
    project_id: "PRJ-2021-260",
    project_name: "Nashville Mixed-Income Housing",
    contract_amount: 2608000,
    actual_cost: 4991000,
    billed_amount: 2592000,
    bid_margin: 0.18,
    realized_margin: -0.91,
    labor_budget: 807000,
    labor_actual: 3819000,
    material_budget: 355000,
    material_actual: 1172000,
    billing_gap: 16000,
    change_orders_count: 9,
    retention_held: 259000,
  },
  {
    project_id: "PRJ-2022-089",
    project_name: "Harbor District Infrastructure",
    contract_amount: 1450000,
    actual_cost: 2132000,
    billed_amount: 1859000,
    bid_margin: 0.15,
    realized_margin: -0.47,
    labor_budget: 580000,
    labor_actual: 1124000,
    material_budget: 320000,
    material_actual: 410000,
    equipment_budget: 145000,
    equipment_actual: 298000,
    billing_gap: 186000,
    change_orders_count: 6,
    retention_held: 145000,
  },
  {
    project_id: "PRJ-2023-142",
    project_name: "Greenfield Solar Array Phase 2",
    contract_amount: 890000,
    actual_cost: 1139000,
    billed_amount: 825000,
    bid_margin: 0.12,
    realized_margin: -0.28,
    labor_budget: 390000,
    labor_actual: 487000,
    material_budget: 285000,
    material_actual: 412000,
    billing_gap: 245000,
    change_orders_count: 3,
    retention_held: 89000,
  },
]

// Utility functions
function formatCurrency(amount: number): string {
  if (amount >= 1000000) {
    return `$${(amount / 1000).toLocaleString()}K`
  }
  return `$${amount.toLocaleString()}`
}

function formatCurrencyShort(amount: number): string {
  return `$${Math.round(amount / 1000)}K`
}

// Risk Scoring
function calculateRiskScore(project: RawProject) {
  const marginDelta = project.bid_margin - project.realized_margin

  let riskScore = 0

  // Margin erosion is the primary signal
  if (marginDelta > 0.50) {
    riskScore += 60
  } else if (marginDelta > 0.25) {
    riskScore += 45
  } else if (marginDelta > 0.15) {
    riskScore += 30
  } else if (marginDelta > 0.05) {
    riskScore += 15
  }

  // Large cost overrun
  const costOverrun = (project.actual_cost - project.contract_amount) / project.contract_amount
  if (costOverrun > 0.5) {
    riskScore += 25
  } else if (costOverrun > 0.25) {
    riskScore += 15
  }

  // Negative margin is critical
  if (project.realized_margin < -0.5) {
    riskScore += 15
  } else if (project.realized_margin < 0) {
    riskScore += 10
  }

  // Determine severity
  const severity: "critical" | "warning" = riskScore >= 60 ? "critical" : "warning"

  return {
    ...project,
    risk_score: Math.min(riskScore, 100),
    is_at_risk: marginDelta > 0.05 || project.realized_margin < 0,
    margin_delta: marginDelta,
    severity,
  }
}

function rankProjectsByRisk(projects: RawProject[]) {
  const scored = projects.map(calculateRiskScore)
  return scored.sort((a, b) => b.risk_score - a.risk_score)
}

// Root Cause Analysis
function analyzeRootCauses(project: RawProject & { is_at_risk?: boolean; margin_delta?: number }): RootCause[] {
  const causes: RootCause[] = []

  // Check labor overrun
  const laborBudget = project.labor_budget ?? 0
  const laborActual = project.labor_actual ?? 0

  if (laborBudget > 0 && laborActual > laborBudget) {
    const multiplier = laborActual / laborBudget
    const overrunPct = (laborActual - laborBudget) / laborBudget

    if (overrunPct > 0.10) {
      causes.push({
        category: "Labor",
        severity: multiplier > 2 ? "critical" : overrunPct > 0.25 ? "high" : "medium",
        overrun_pct: Math.round(overrunPct * 100),
        overrun_dollars: laborActual - laborBudget,
        overrun_multiplier: Math.round(multiplier * 10) / 10,
        estimated: laborBudget,
        actual: laborActual,
        explanation: `${formatCurrencyShort(laborActual)} actual vs ${formatCurrencyShort(laborBudget)} estimated — ${multiplier.toFixed(1)}x overrun.`,
        details: multiplier > 4 
          ? `Crew ramped to 12-18 workers/day through peak phase; estimate assumed 5-8.`
          : multiplier > 2
          ? `${Math.round((multiplier - 1) * 10)} additional site surveys performed outside original scope; crews worked weekends for ${Math.round(multiplier * 3)} weeks.`
          : `6-week schedule slip required overtime to meet deadline; premium rates not recovered.`,
      })
    }
  }

  // Check material overrun
  const materialBudget = project.material_budget ?? 0
  const materialActual = project.material_actual ?? 0

  if (materialBudget > 0 && materialActual > materialBudget) {
    const multiplier = materialActual / materialBudget
    const overrunPct = (materialActual - materialBudget) / materialBudget

    if (overrunPct > 0.10) {
      causes.push({
        category: "Material",
        severity: multiplier > 2 ? "critical" : overrunPct > 0.25 ? "high" : "medium",
        overrun_pct: Math.round(overrunPct * 100),
        overrun_dollars: materialActual - materialBudget,
        overrun_multiplier: Math.round(multiplier * 10) / 10,
        estimated: materialBudget,
        actual: materialActual,
        explanation: `${formatCurrencyShort(materialActual)} actual vs ${formatCurrencyShort(materialBudget)} estimated — ${multiplier.toFixed(1)}x overrun.`,
        details: multiplier > 2
          ? `Late-stage delivery clustering suggests expediting and substitutions.`
          : `Steel price escalation of 18% not passed through; escalation clause exists but was not activated.`,
      })
    }
  }

  // Check equipment overrun
  const equipmentBudget = project.equipment_budget ?? 0
  const equipmentActual = project.equipment_actual ?? 0

  if (equipmentBudget > 0 && equipmentActual > equipmentBudget) {
    const multiplier = equipmentActual / equipmentBudget
    const overrunPct = (equipmentActual - equipmentBudget) / equipmentBudget

    if (overrunPct > 0.10) {
      causes.push({
        category: "Equipment",
        severity: overrunPct > 0.5 ? "high" : "medium",
        overrun_pct: Math.round(overrunPct * 100),
        overrun_dollars: equipmentActual - equipmentBudget,
        overrun_multiplier: Math.round(multiplier * 10) / 10,
        estimated: equipmentBudget,
        actual: equipmentActual,
        explanation: `${formatCurrencyShort(equipmentActual)} actual vs ${formatCurrencyShort(equipmentBudget)} estimated — ${multiplier.toFixed(1)}x overrun.`,
        details: `Extended rental periods due to weather delays; no force majeure clause invoked.`,
      })
    }
  }

  return causes
}

// Recommendations
function generateRecommendations(project: RawProject & { margin_delta?: number }, rootCauses: RootCause[]): Recommendation[] {
  const recommendations: Recommendation[] = []

  // Check for CO audit opportunity
  const coCount = project.change_orders_count ?? 0
  const laborMultiplier = project.labor_actual / project.labor_budget
  
  if (coCount > 0 && laborMultiplier > 1.5) {
    const laborCauses = rootCauses.filter(c => c.category === "Labor")
    const crewExpansions = Math.max(1, Math.round(laborMultiplier))
    
    recommendations.push({
      action: "AUDIT_CHANGE_ORDERS",
      priority: "high",
      dollar_impact: null,
      description: `Audit ${coCount} approved COs for unexecuted scope — if any work was performed without documented contract relief, submit supplemental CO immediately.`,
      details: `Labor logs show ${crewExpansions} crew expansions with no CO trigger.`,
    })
  }

  // Labor-specific recommendations
  for (const cause of rootCauses) {
    if (cause.category === "Labor" && cause.overrun_multiplier && cause.overrun_multiplier > 1.5) {
      recommendations.push({
        action: "REVIEW_FIELD_NOTES",
        priority: "high",
        dollar_impact: cause.overrun_dollars ?? null,
        description: `Review field notes for references to owner-directed work outside original scope (labor logs show ${Math.round(cause.overrun_multiplier!)} crew expansions with no CO trigger).`,
        details: "",
      })
      break
    }
  }

  // Material escalation clause
  const materialCause = rootCauses.find(c => c.category === "Material")
  if (materialCause && materialCause.overrun_multiplier && materialCause.overrun_multiplier > 1.2) {
    recommendations.push({
      action: "ESCALATION_CLAUSE",
      priority: "high",
      dollar_impact: materialCause.overrun_dollars ?? null,
      description: `Activate material escalation clause in Section 7.3 — steel index increase of 18% exceeds 10% threshold.`,
      details: "",
    })
  }

  // Equipment/weather recommendations
  const equipmentCause = rootCauses.find(c => c.category === "Equipment")
  if (equipmentCause) {
    recommendations.push({
      action: "FORCE_MAJEURE",
      priority: "medium",
      dollar_impact: equipmentCause.overrun_dollars ?? null,
      description: `Submit force majeure claim for 23 weather delay days — met threshold of 5+ consecutive days twice.`,
      details: "",
    })
  }

  // Billing acceleration
  const billingGap = project.billing_gap ?? 0
  if (billingGap > 50000) {
    recommendations.push({
      action: "ACCELERATE_BILLING",
      priority: "high",
      dollar_impact: billingGap,
      description: `Accelerate remaining billing: ${formatCurrency(billingGap)} unbilled work completed; submit invoice within 10 days.`,
      details: "",
    })
  }

  // Retention release opportunity
  const retention = project.retention_held ?? 0
  const billingCompletion = (project.billed_amount / project.actual_cost) * 100
  if (retention > 0 && billingCompletion > 90) {
    recommendations.push({
      action: "RETENTION_RELEASE",
      priority: "medium",
      dollar_impact: retention,
      description: `Engage GC on retention release: ${formatCurrency(retention)} held. Release accelerates cash recovery on a completed project.`,
      details: "",
    })
  }

  // Value engineering for remaining scope
  if (billingGap > 100000) {
    recommendations.push({
      action: "VALUE_ENGINEERING",
      priority: "medium",
      dollar_impact: null,
      description: `Review remaining scope for value engineering opportunities — ${formatCurrency(billingGap)} of work remains.`,
      details: "",
    })
  }

  // Document weather delays
  if (rootCauses.some(c => c.details?.toLowerCase().includes("weather") || c.details?.toLowerCase().includes("schedule"))) {
    recommendations.push({
      action: "DOCUMENT_DELAYS",
      priority: "medium",
      dollar_impact: null,
      description: `Document weather delays for potential schedule relief — 4 days in April exceeded regional rainfall averages.`,
      details: "",
    })
  }

  return recommendations.slice(0, 3) // Limit to 3 recommendations per project
}

// Main Report Generator
export function generateAgentReport(topN: number = 10): AgentReport {
  const ranked = rankProjectsByRisk(MOCK_PROJECTS)
  const atRisk = ranked.filter((p) => p.is_at_risk).slice(0, topN)

  const analyzedProjects: Project[] = []
  let totalRecoverable = 0

  for (const project of atRisk) {
    const causes = analyzeRootCauses(project)
    const recs = generateRecommendations(project, causes)
    const projectRecoverable = recs.reduce((sum, r) => sum + (r.dollar_impact ?? 0), 0)
    totalRecoverable += projectRecoverable

    const billingCompletion = project.actual_cost > 0 
      ? (project.billed_amount / project.actual_cost)
      : 1

    analyzedProjects.push({
      project_id: project.project_id,
      project_name: project.project_name,
      risk_score: project.risk_score,
      severity: project.severity,
      contract_amount: project.contract_amount,
      actual_cost: project.actual_cost,
      billed_amount: project.billed_amount,
      bid_margin: project.bid_margin,
      realized_margin: project.realized_margin,
      margin_delta: project.margin_delta,
      labor_budget: project.labor_budget,
      labor_actual: project.labor_actual,
      material_budget: project.material_budget,
      material_actual: project.material_actual,
      equipment_budget: project.equipment_budget,
      equipment_actual: project.equipment_actual,
      billing_gap: project.billing_gap,
      billing_completion: billingCompletion,
      change_orders_count: project.change_orders_count,
      retention_held: project.retention_held,
      root_causes: causes,
      recommendations: recs,
      recoverable_amount: projectRecoverable,
    })
  }

  return {
    summary: {
      total_projects_analyzed: 847, // Simulate larger portfolio
      projects_at_risk: atRisk.length,
      total_recoverable_amount: totalRecoverable,
    },
    projects: analyzedProjects,
  }
}
