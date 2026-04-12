import { NextResponse } from "next/server"

export async function GET() {
  try {
    const res = await fetch("http://127.0.0.1:8000/api/analyze", {
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
      { error: "Backend connection failed" },
      { status: 500 }
    )
  }
}