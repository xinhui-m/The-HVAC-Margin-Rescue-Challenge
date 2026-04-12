"use client"

import useSWR from "swr"
import { Header } from "./header"
import { Greeting } from "./greeting"
import { SummaryCards } from "./summary-cards"
import { ProjectList } from "./project-list"
import { Spinner } from "@/components/ui/spinner"
import { AlertCircle, RefreshCw, Sparkles } from "lucide-react"
import { Button } from "@/components/ui/button"
import type { AgentReport } from "@/lib/types"

const fetcher = (url: string) => fetch(url).then((res) => res.json())

export function Dashboard() {
  const { data, error, isLoading, mutate } = useSWR<AgentReport>(
    "/api/analyze",
    fetcher,
    {
      revalidateOnFocus: false,
    }
  )

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <div className="flex min-h-[400px] items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <Spinner className="h-8 w-8 text-primary" />
            <p className="text-muted-foreground">Agent analyzing projects...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <div className="flex min-h-[400px] items-center justify-center">
          <div className="flex flex-col items-center gap-4 text-center">
            <AlertCircle className="h-12 w-12 text-destructive" />
            <div>
              <p className="font-medium text-foreground">Failed to load analysis</p>
              <p className="mt-1 text-sm text-muted-foreground">
                Something went wrong. Please try again.
              </p>
            </div>
            <Button onClick={() => mutate()} variant="outline" size="sm">
              <RefreshCw className="mr-2 h-4 w-4" />
              Retry
            </Button>
          </div>
        </div>
      </div>
    )
  }

  if (!data) {
    return null
  }

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main className="mx-auto max-w-5xl px-6 py-8">
        <div className="space-y-6">
          <Greeting totalProjects={data.summary.total_projects_analyzed} />

          <SummaryCards summary={data.summary} projects={data.projects} />

          <div>
            <div className="mb-4 flex items-center gap-2">
              <h2 className="text-lg font-semibold text-foreground">
                Projects that need attention
              </h2>
              <span className="text-sm text-muted-foreground">
                sorted by severity
              </span>
            </div>
            <ProjectList projects={data.projects} />
          </div>

          <div className="flex items-center justify-center gap-2 py-4 text-sm text-muted-foreground">
            <Sparkles className="h-4 w-4" />
            <span>Data from Deltek Vision, Procore, SAP</span>
          </div>
        </div>
      </main>
    </div>
  )
}