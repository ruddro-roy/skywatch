/**
 * Edge route: /api/geoip
 *
 * Privacy guarantee:
 * - IP is extracted from request headers and forwarded to FastAPI once
 * - The IP is NEVER written to any log, database, or response
 * - Only city-level location is returned to the client
 * - If geolocation fails, returns null (client falls back to manual picker)
 */

import { NextRequest, NextResponse } from "next/server";

export const runtime = "edge";

export async function GET(request: NextRequest) {
  // Extract IP from standard proxy headers (Vercel, Cloudflare, nginx)
  // Precedence: CF-Connecting-IP > X-Real-IP > X-Forwarded-For > remote address
  const cfIp = request.headers.get("cf-connecting-ip");
  const realIp = request.headers.get("x-real-ip");
  const forwardedFor = request.headers.get("x-forwarded-for");

  const ip =
    cfIp ??
    realIp ??
    forwardedFor?.split(",")[0]?.trim() ??
    null;

  // Forward to FastAPI backend which handles the actual geolocation
  // (keeps the lookup logic in one place, easier to swap providers)
  const apiBase =
    process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

  try {
    const response = await fetch(`${apiBase}/api/geoip`, {
      headers: {
        // Forward the IP so FastAPI can resolve it
        // This is the ONLY place the IP travels — FastAPI discards it after lookup
        "x-client-ip": ip ?? "",
        "content-type": "application/json",
      },
      // Short timeout — geolocation should be fast
      signal: AbortSignal.timeout(5000),
    });

    if (!response.ok) {
      return NextResponse.json(null, { status: 200 });
    }

    const data = await response.json();

    // CRITICAL: Strip the IP from the response before returning to the client
    // The client receives only: { city, country, country_code, region, lat, lon }
    const { city, country, country_code, region, lat, lon } = data;

    return NextResponse.json(
      { city, country, country_code, region, lat, lon },
      {
        headers: {
          // No caching — fresh lookup on each page load
          "Cache-Control": "no-store, no-cache, must-revalidate",
        },
      }
    );
  } catch {
    // Geolocation failure is non-fatal — client shows manual picker
    return NextResponse.json(null, { status: 200 });
  }
}
