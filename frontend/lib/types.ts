export interface RootCause {
  category: string
  severity: string
  overrun_pct?: number
  overrun_dollars?: number
  overrun_multiplier?: number
  estimated?: number
  actual?: number
  gap_dollars?: number
  billing_completion?: number
  explanation: string
  details?: string
}

export interface Recommendation {
  action: string
  priority: string
  dollar_impact: number | null
  description: string
  details: string
}

export interface Project {
  project_id: string
  project_name: string
  risk_score: number
  severity: "critical" | "warning"
  contract_amount: number
  actual_cost: number
  billed_amount: number
  bid_margin: number
  realized_margin: number
  margin_delta: number
  labor_budget: number
  labor_actual: number
  material_budget: number
  material_actual: number
  equipment_budget?: number
  equipment_actual?: number
  billing_gap: number
  billing_completion: number
  change_orders_count?: number
  retention_held?: number
  root_causes: RootCause[]
  recommendations: Recommendation[]
  recoverable_amount: number
}

export interface Summary {
  total_projects_analyzed: number
  projects_at_risk: number
  total_recoverable_amount: number
}

export interface AgentReport {
  summary: Summary
  projects: Project[]
}
