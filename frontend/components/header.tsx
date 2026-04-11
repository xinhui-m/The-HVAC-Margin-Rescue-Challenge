"use client"

import { Sparkles } from "lucide-react"

export function Header() {
  return (
    <header className="flex items-center justify-between border-b border-border bg-card px-6 py-4">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
          <Sparkles className="h-5 w-5 text-primary" />
        </div>
        <div>
          <h1 className="font-semibold text-foreground">MarginGuard</h1>
          <p className="text-sm text-muted-foreground">Know before the margin is gone.</p>
        </div>
      </div>
      <div className="flex items-center gap-2 rounded-full border border-green-200 bg-green-50 px-3 py-1">
        <span className="h-2 w-2 rounded-full bg-green-500" />
        <span className="text-sm font-medium text-green-700">Online</span>
      </div>
    </header>
  )
}
