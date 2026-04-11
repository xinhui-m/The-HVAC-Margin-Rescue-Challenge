"use client"

import { Card, CardContent } from "@/components/ui/card"

interface GreetingProps {
  totalProjects: number
}

export function Greeting({ totalProjects }: GreetingProps) {
  const hour = new Date().getHours()
  const greeting = hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening"

  return (
    <Card className="border-border bg-card">
      <CardContent className="flex items-start gap-3 p-6">
        <span className="text-2xl">{`<3`}</span>
        <div>
          <p className="font-semibold text-foreground">{greeting}!</p>
          <p className="text-muted-foreground">
            I scanned <span className="font-semibold text-foreground">{totalProjects} projects</span>
            {" "}while you were away. Found a few things that need your attention.
            {" "}Here&apos;s the quick summary:
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
