"use client"

import { Card, CardContent } from "@/components/ui/card"
import { DollarSign, AlertOctagon, AlertTriangle, BarChart3 } from "lucide-react"
import type { AgentReport } from "@/lib/types"

interface SummaryCardsProps {
  summary: AgentReport["summary"]
  projects: AgentReport["projects"]
}

export function SummaryCards({ summary, projects }: SummaryCardsProps) {
  const criticalCount = projects.filter(p => p.severity === "critical").length
  const warningCount = projects.filter(p => p.severity === "warning").length
  
  const avgMargin = projects.length > 0
    ? projects.reduce((acc, p) => acc + p.realized_margin, 0) / projects.length
    : 0

  const formatCurrency = (value: number) => {
    if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(2)}M`
    }
    return `$${(value / 1000).toFixed(0)}K`
  }

  return (
    <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
      <Card className="border-yellow-200 bg-yellow-50">
        <CardContent className="p-4">
          <div className="mb-2 flex h-8 w-8 items-center justify-center rounded bg-yellow-100">
            <DollarSign className="h-5 w-5 text-yellow-600" />
          </div>
          <p className="text-sm font-medium text-yellow-700">At Risk</p>
          <p className="text-2xl font-bold text-yellow-600">
            {formatCurrency(summary.total_recoverable_amount)}
          </p>
        </CardContent>
      </Card>

      <Card className="border-red-200 bg-red-50">
        <CardContent className="p-4">
          <div className="mb-2 flex h-8 w-8 items-center justify-center rounded bg-red-100">
            <AlertOctagon className="h-5 w-5 text-red-600" />
          </div>
          <p className="text-sm font-medium text-red-700">Critical</p>
          <p className="text-2xl font-bold text-red-600">
            {criticalCount} project{criticalCount !== 1 ? "s" : ""}
          </p>
        </CardContent>
      </Card>

      <Card className="border-orange-200 bg-orange-50">
        <CardContent className="p-4">
          <div className="mb-2 flex h-8 w-8 items-center justify-center rounded bg-orange-100">
            <AlertTriangle className="h-5 w-5 text-orange-600" />
          </div>
          <p className="text-sm font-medium text-orange-700">Warning</p>
          <p className="text-2xl font-bold text-orange-600">
            {warningCount} project{warningCount !== 1 ? "s" : ""}
          </p>
        </CardContent>
      </Card>

      <Card className="border-border bg-card">
        <CardContent className="p-4">
          <div className="mb-2 flex h-8 w-8 items-center justify-center rounded bg-muted">
            <BarChart3 className="h-5 w-5 text-muted-foreground" />
          </div>
          <p className="text-sm font-medium text-muted-foreground">Avg Margin</p>
          <p className="text-2xl font-bold text-foreground">
            {(avgMargin * 100).toFixed(0)}%
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
