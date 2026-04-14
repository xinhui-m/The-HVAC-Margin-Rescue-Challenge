import { NextResponse } from "next/server"

export async function GET() {
  try {
    const backendUrl = process.env.BACKEND_API_URL

    if (!backendUrl) {
      return NextResponse.json(
        { error: "BACKEND_API_URL is not set" },
        { status: 500 }
      )
    }

    const res = await fetch(`${backendUrl}/api/analyze`, {
      cache: "no-store",
    })

    if (!res.ok) {
      return NextResponse.json(
        { error: "Failed to fetch from backend" },
        { status: res.status }
      )
    }

    const data = await res.json()
    return NextResponse.json(data)
  } catch (error) {
    return NextResponse.json(
      {
        error: "Backend connection failed",
        details: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    )
  }
}