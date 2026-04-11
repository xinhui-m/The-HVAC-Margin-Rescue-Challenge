import { NextResponse } from "next/server"
import { generateAgentReport } from "@/lib/agent"

export async function GET() {
  const report = generateAgentReport()
  return NextResponse.json(report)
}
