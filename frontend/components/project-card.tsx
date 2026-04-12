"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ChevronDown, ChevronUp, AlertOctagon, AlertTriangle, Sparkles } from "lucide-react"
import type { Project } from "@/lib/types"

interface ProjectCardProps {
  project: Project
}

// Safe currency formatter
function formatCurrency(amount?: number | null): string {
  if (amount === null || amount === undefined || Number.isNaN(amount)) {
    return "$0"
  }

  if (Math.abs(amount) >= 1000000) {
    return `$${(amount / 1000000).toFixed(1)}M`
  }

  if (Math.abs(amount) >= 1000) {
    return `$${(amount / 1000).toFixed(1)}K`
  }

  return `$${amount.toLocaleString()}`
}

export function ProjectCard({ project }: ProjectCardProps) {
  const [expanded, setExpanded] = useState(false)

  // Use real backend logic
  const isCritical = project.realized_margin < 0

  const bgColor = isCritical ? "bg-red-50 border-red-200" : "bg-amber-50 border-amber-200"
  const iconColor = isCritical ? "text-red-500" : "text-amber-500"
  const labelColor = isCritical ? "text-red-600" : "text-amber-600"
  const Icon = isCritical ? AlertOctagon : AlertTriangle

  return (
    <Card className={`${bgColor} overflow-hidden`}>
      <CardContent className="p-6">
        {/* Header */}
        <div className="flex items-start gap-3">
          <div className={`mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${isCritical ? "bg-red-100" : "bg-amber-100"}`}>
            <Icon className={`h-4 w-4 ${iconColor}`} />
          </div>

          <div className="flex-1 min-w-0">
            {/* Title */}
            <div className="flex items-center gap-2 flex-wrap">
              <span className={`text-sm font-bold uppercase ${labelColor}`}>
                {isCritical ? "CRITICAL" : "WARNING"}
              </span>
              <span className="text-muted-foreground">—</span>
              <span className="font-mono text-sm font-semibold text-foreground">
                {project.project_id}
              </span>
              <span className="text-muted-foreground">|</span>
              <span className="text-sm font-medium text-foreground">
                {project.project_name}
              </span>
            </div>

            {/* Key Metrics */}
            <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 font-mono text-sm">
              <div>
                <span className="text-muted-foreground">Recoverable:</span>{" "}
                <span className="font-semibold text-foreground">
                  {formatCurrency(project.recoverable_amount)}
                </span>
              </div>

              <div>
                <span className="text-muted-foreground">Margin:</span>{" "}
                <span className={`font-semibold ${project.realized_margin < 0 ? "text-red-600" : "text-foreground"}`}>
                  {(project.realized_margin * 100).toFixed(0)}%
                </span>
              </div>

              <div>
                <span className="text-muted-foreground">Risk Score:</span>{" "}
                <span className="font-semibold text-foreground">
                  {project.risk_score}
                </span>
              </div>
            </div>

            {/* Expand button */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setExpanded(!expanded)}
              className="mt-2 h-auto p-0 text-sm font-medium text-foreground hover:bg-transparent hover:underline"
            >
              {expanded ? (
                <>
                  <ChevronUp className="mr-1 h-4 w-4" />
                  Hide details
                </>
              ) : (
                <>
                  <ChevronDown className="mr-1 h-4 w-4" />
                  Show root causes & recommendations
                </>
              )}
            </Button>

            {/* Expanded section */}
            {expanded && (
              <div className="mt-4 space-y-4">

                {/* Root Causes */}
                <div>
                  <h4 className="font-semibold text-foreground">Root causes:</h4>
                  <ul className="mt-2 space-y-2 text-sm">
                    {project.root_causes.map((cause, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <span className="text-muted-foreground select-none">•</span>
                        <span className="text-foreground">
                          <span className="font-semibold">
                            {cause.type.replace("_", " ")}:
                          </span>{" "}
                          {cause.explanation}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Recommendations */}
                <div>
                  <h4 className="font-semibold text-foreground">Recovery actions:</h4>
                  <ol className="mt-2 space-y-2 text-sm">
                    {project.recommendations.map((rec, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <span className="font-semibold text-foreground">{idx + 1}.</span>
                        <span className="text-foreground">{rec.action}</span>
                      </li>
                    ))}
                  </ol>
                </div>

                {/* Footer */}
                <div className="flex items-center gap-2 pt-2 text-xs text-muted-foreground">
                  <Sparkles className="h-3 w-3" />
                  <span>Analysis generated by Margin Intelligence</span>
                </div>

              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}