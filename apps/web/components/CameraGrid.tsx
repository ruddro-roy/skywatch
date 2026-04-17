"use client";

/**
 * CameraGrid — Nearby public webcams with CV-detected condition labels
 *
 * Legal notice: Only shows cameras from permitted sources:
 * - Windy Webcams API (ToS-compliant)
 * - US DOT 511 (public domain)
 * - NOAA/NWS (public domain)
 * NEVER shows cameras from Insecam, Opentopia, or similar unsecured sources.
 */

import Image from "next/image";
import type { CameraResponse, Location } from "@/lib/api";
import { conditionColor } from "@/lib/api";

interface CameraGridProps {
  cameras: CameraResponse | null;
  loading: boolean;
  location: Location | null;
}

const CONDITION_LABELS: Record<string, string> = {
  clear: "Clear",
  cloudy: "Cloudy",
  fog: "Foggy",
  rain: "Rain",
  snow: "Snow",
  unknown: "Unknown",
};

const CONDITION_BG: Record<string, string> = {
  clear: "bg-amber-900/80 border-amber-700/50",
  cloudy: "bg-slate-800/90 border-slate-600/50",
  fog: "bg-slate-700/80 border-slate-500/50",
  rain: "bg-blue-900/80 border-blue-700/50",
  snow: "bg-sky-900/80 border-sky-700/50",
  unknown: "bg-slate-900/80 border-slate-700/50",
};

const METHOD_LABELS: Record<string, string> = {
  heuristic: "HSV heuristic",
  efficientnet: "EfficientNet-B0",
  clip: "CLIP zero-shot",
  unavailable: "No image",
};

const SOURCE_ATTRIBUTION: Record<string, string> = {
  windy: "Windy.com",
  dot_us: "US DOT 511",
  noaa: "NOAA/NWS",
};

export function CameraGrid({ cameras, loading, location }: CameraGridProps) {
  if (loading) {
    return (
      <div className="sw-card">
        <div className="skeleton mb-4 h-5 w-48 rounded" />
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="skeleton aspect-video rounded-lg" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="sw-card animate-slide-up">
      <div className="mb-4 flex items-start justify-between">
        <div>
          <h2 className="text-sm font-medium text-slate-300">
            Nearby Cameras
            {cameras?.total != null && cameras.total > 0 && (
              <span className="ml-2 text-slate-500">
                ({cameras.total} found within {cameras.radius_km} km)
              </span>
            )}
          </h2>
          <p className="mt-0.5 text-xs text-slate-500">
            Conditions detected via computer vision · Only legally-accessible public sources
          </p>
        </div>

        {/* Legal notice badge */}
        <span className="shrink-0 rounded-full bg-green-900/30 border border-green-700/30 px-2.5 py-0.5 text-xs text-green-400">
          ✓ ToS-compliant sources only
        </span>
      </div>

      {!cameras || cameras.cameras.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-700 bg-slate-800/30 py-12 text-center">
          <div className="text-3xl mb-3">📷</div>
          <p className="text-sm text-slate-400 mb-1">No cameras found nearby</p>
          <p className="text-xs text-slate-500">
            {location
              ? `No public webcams within ${cameras?.radius_km ?? 50} km of ${location.city}`
              : "Configure a WINDY_API_KEY to enable global webcam coverage"}
          </p>
          <p className="mt-3 text-xs text-slate-600">
            Add a Windy API key in .env to discover webcams globally
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
          {cameras.cameras.map((cam) => (
            <div
              key={cam.id}
              className="group relative overflow-hidden rounded-lg border border-slate-700/50 bg-slate-800/50 hover:border-sky-700/50 transition-colors"
            >
              {/* Camera thumbnail */}
              <div className="relative aspect-video bg-slate-900">
                {cam.thumbnail_url ? (
                  <Image
                    src={cam.thumbnail_url}
                    alt={cam.name}
                    fill
                    className="object-cover"
                    unoptimized // External URLs — skip Next.js optimization for webcam frames
                    onError={() => {
                      // Image load failed — handled by the empty state below
                    }}
                  />
                ) : (
                  <div className="flex h-full items-center justify-center text-slate-600">
                    <svg className="h-8 w-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                      <path d="M15 10l4.553-2.069A1 1 0 0 1 21 8.82v6.36a1 1 0 0 1-1.447.89L15 14M5 18h8a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2z"/>
                    </svg>
                  </div>
                )}

                {/* CV condition badge overlay */}
                {cam.condition && cam.condition.label !== "unknown" && (
                  <div
                    className={`absolute bottom-1.5 left-1.5 flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium backdrop-blur-sm ${
                      CONDITION_BG[cam.condition.label] ?? CONDITION_BG.unknown
                    }`}
                  >
                    <span className={conditionColor(cam.condition.label)}>
                      {CONDITION_LABELS[cam.condition.label]}
                    </span>
                    <span className="text-slate-500">
                      {Math.round(cam.condition.confidence * 100)}%
                    </span>
                  </div>
                )}
              </div>

              {/* Camera info */}
              <div className="p-2">
                <p className="text-xs font-medium text-slate-200 truncate">{cam.name}</p>
                <div className="mt-1 flex items-center justify-between">
                  <span className="text-xs text-slate-500">
                    {cam.distance_km.toFixed(1)} km away
                  </span>
                  {cam.condition && (
                    <span className="text-xs text-slate-600">
                      {METHOD_LABELS[cam.condition.method] ?? cam.condition.method}
                    </span>
                  )}
                </div>

                {/* Attribution */}
                <div className="mt-1.5 flex items-center gap-1.5">
                  <span className="provider-tag text-slate-500">
                    {SOURCE_ATTRIBUTION[cam.source] ?? cam.source}
                  </span>
                  {cam.attribution_url && (
                    <a
                      href={cam.attribution_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-sky-600 hover:text-sky-500"
                    >
                      ↗
                    </a>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
