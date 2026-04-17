"use client";

/**
 * CameraGrid, nearby public webcams with CV-detected condition labels.
 * Classic light theme. No emoji. Only legally-accessible public sources.
 */

import Image from "next/image";
import type { CameraResponse, Location } from "@/lib/api";

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

const METHOD_LABELS: Record<string, string> = {
  heuristic: "HSV heuristic",
  efficientnet: "EfficientNet-B0",
  clip: "CLIP zero-shot",
  unavailable: "No image",
};

const SOURCE_ATTRIBUTION: Record<string, string> = {
  windy: "Windy.com",
  dot_us: "US DOT 511",
  noaa: "NOAA / NWS",
};

export function CameraGrid({ cameras, loading, location }: CameraGridProps) {
  if (loading) {
    return (
      <div className="sw-card">
        <div className="skeleton mb-4 h-4 w-48" />
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="skeleton aspect-video" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="sw-card">
      <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="sw-card-heading">
            Nearby cameras
            {cameras?.total != null && cameras.total > 0 && (
              <span className="ml-2 normal-case tracking-normal text-ink-faint">
                ({cameras.total} within {cameras.radius_km} km)
              </span>
            )}
          </div>
          <p className="font-sans text-xs text-ink-mute">
            Conditions detected via computer vision. Public sources only.
          </p>
        </div>
        <span className="live-pill">Public sources only</span>
      </div>

      {!cameras || cameras.cameras.length === 0 ? (
        <div className="rounded border border-dashed border-rule bg-paper-panel py-10 text-center">
          <p className="mb-1 font-sans text-sm text-ink-soft">
            No cameras found nearby
          </p>
          <p className="font-sans text-xs text-ink-mute">
            {location
              ? `No public webcams within ${cameras?.radius_km ?? 50} km of ${location.city}`
              : "Configure a WINDY_API_KEY to enable global webcam coverage"}
          </p>
          <p className="mt-2 font-sans text-xs text-ink-faint">
            Add a Windy API key in <code className="font-mono">.env</code> to enable global webcam lookup.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
          {cameras.cameras.map((cam) => (
            <div
              key={cam.id}
              className="group overflow-hidden rounded border border-rule bg-paper-raised"
            >
              <div className="relative aspect-video bg-paper-panel">
                {cam.thumbnail_url ? (
                  <Image
                    src={cam.thumbnail_url}
                    alt={cam.name}
                    fill
                    className="object-cover"
                    unoptimized
                  />
                ) : (
                  <div className="flex h-full items-center justify-center font-sans text-xs text-ink-faint">
                    No image
                  </div>
                )}

                {cam.condition && cam.condition.label !== "unknown" && (
                  <div className="absolute bottom-1.5 left-1.5 flex items-center gap-1.5 rounded-sm border border-rule bg-paper-raised/90 px-2 py-0.5 font-sans text-xs text-ink-soft backdrop-blur-sm">
                    <span className="font-medium">
                      {CONDITION_LABELS[cam.condition.label]}
                    </span>
                    <span className="sw-num text-ink-mute">
                      {Math.round(cam.condition.confidence * 100)}%
                    </span>
                  </div>
                )}
              </div>

              <div className="p-2.5">
                <p className="truncate font-sans text-xs font-medium text-ink">
                  {cam.name}
                </p>
                <div className="mt-1 flex items-center justify-between font-sans text-xs text-ink-mute">
                  <span className="sw-num">{cam.distance_km.toFixed(1)} km</span>
                  {cam.condition && (
                    <span className="text-ink-faint">
                      {METHOD_LABELS[cam.condition.method] ?? cam.condition.method}
                    </span>
                  )}
                </div>
                <div className="mt-2 flex items-center gap-1.5">
                  <span className="provider-tag">
                    {SOURCE_ATTRIBUTION[cam.source] ?? cam.source}
                  </span>
                  {cam.attribution_url && (
                    <a
                      href={cam.attribution_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-sans text-xs"
                    >
                      Source
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
