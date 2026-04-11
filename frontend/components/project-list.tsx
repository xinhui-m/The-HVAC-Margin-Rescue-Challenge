"use client"

import { ProjectCard } from "./project-card"
import type { Project } from "@/lib/types"

interface ProjectListProps {
  projects: Project[]
}

export function ProjectList({ projects }: ProjectListProps) {
  if (projects.length === 0) {
    return (
      <div className="rounded-lg border border-border bg-card p-8 text-center">
        <p className="text-muted-foreground">No at-risk projects found.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {projects.map((project) => (
        <ProjectCard key={project.project_id} project={project} />
      ))}
    </div>
  )
}
