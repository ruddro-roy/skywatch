"use client";

/**
 * EnsembleConfidence — Visualises provider weights and ensemble agreement
 *
 * Shows:
 * - Which forecast providers are active
 * - Their relative weights
 * - Ensemble confidence (1 − normalised std dev)
 * - Std deviation in degrees
 */

import type { WeatherResponse } from "@/lib/api";

interface EnsembleConfidenceProps {
  weather: WeatherResponse | null;
  loading: boolean;
}

const PROVIDER_DISPLAY: Record<string, { label: string; color: string; url: string }> = {
  open_meteo: {
    label: "Open-Meteo (ECMWF IFS)",
    color: "#0ea5e9",
    url: "https://open-meteo.com",
  },
  openweathermap: {
    label: "OpenWeatherMap (GFS)",
    color: "#f59e0b",
    url: "https://openweathermap.org",
  },
  nvidia_earth2: {
    label: "NVIDIA Earth-2 (FourCastNet)",
    color: "#76b900",
    url: "https://docs.api.nvidia.com/nim/reference/nvidia-fourcastnet",
  },
  metnet: {
    label: "Google MetNet-3",
    color: "#4285f4",
    url: "https://cloud.google.com/blog/topics/developers-practitioners/metnet-3-google-deepminds-weather-model",
  },
};

function ConfidenceBar({ value }: { value: number }) {
  const percentage = Math.round(value * 100);
  const color =
    percentage >= 80 ? "#22c55e" : percentage >= 60 ? "#f59e0b" : "#ef4444";

  return (
    <div className="relative h-2.5 w-full overflow-hidden rounded-full bg-slate-700">
      <div
        className="h-full rounded-full transition-all duration-700"
        style={{ width: `${percentage}%`, backgroundColor: color }}
      />
    </div>
  );
}

export function EnsembleConfidence({
  weather,
  loading,
}: EnsembleConfidenceProps) {
  if (loading) {
    return (
      <div className="sw-card h-full">
        <div className="skeleton mb-3 h-5 w-40 rounded" />
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i}>
              <div className="skeleton mb-1.5 h-3 w-32 rounded" />
              <div className="skeleton h-2.5 w-full rounded" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (!weather?.ensemble) {
    return (
      <div className="sw-card h-full flex items-center justify-center text-slate-500 text-sm">
        No ensemble data
      </div>
    );
  }

  const { ensemble } = weather;
  const confidence = Math.round(ensemble.confidence * 100);
  const activeProviders = ensemble.provider_results?.filter((p) => p.available) ?? [];
  const totalWeight = activeProviders.reduce((sum, p) => sum + p.weight, 0);

  return (
    <div className="sw-card h-full animate-slide-up">
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <h2 className="text-sm font-medium text-slate-300">Ensemble Confidence</h2>
          <p className="mt-0.5 text-xs text-slate-500">
            Weighted agreement across {activeProviders.length} active model
            {activeProviders.length !== 1 ? "s" : ""}
          </p>
        </div>
        <div className="text-right shrink-0">
          <div
            className={`text-2xl font-bold ${
              confidence >= 80
                ? "text-green-400"
                : confidence >= 60
                ? "text-amber-400"
                : "text-red-400"
            }`}
          >
            {confidence}%
          </div>
          <div className="text-xs text-slate-500">
            ±{ensemble.std_dev?.toFixed(1) ?? "—"}°C spread
          </div>
        </div>
      </div>

      {/* Overall confidence bar */}
      <div className="mb-5">
        <ConfidenceBar value={ensemble.confidence} />
        <div className="mt-1 flex justify-between text-xs text-slate-500">
          <span>Low agreement</span>
          <span>High agreement</span>
        </div>
      </div>

      {/* Per-provider breakdown */}
      <div className="space-y-3">
        {ensemble.provider_results?.map((result) => {
          const display =
            PROVIDER_DISPLAY[result.provider] ?? {
              label: result.provider,
              color: "#64748b",
              url: "#",
            };
          const weightPct =
            totalWeight > 0
              ? Math.round((result.weight / totalWeight) * 100)
              : 0;

          return (
            <div key={result.provider}>
              <div className="mb-1.5 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span
                    className="h-2 w-2 rounded-full"
                    style={{ backgroundColor: display.color }}
                  />
                  <a
                    href={display.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-slate-400 hover:text-slate-200 transition-colors"
                  >
                    {display.label}
                  </a>
                  {!result.available && (
                    <span className="rounded bg-slate-700 px-1.5 py-0.5 text-xs text-slate-400">
                      inactive
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2 text-xs">
                  {result.available && (
                    <span className="text-slate-400">
                      {Math.round(result.temperature_2m)}°C
                    </span>
                  )}
                  <span className="text-slate-500">{weightPct}% weight</span>
                </div>
              </div>
              {result.available && (
                <div className="relative h-1.5 w-full overflow-hidden rounded-full bg-slate-700">
                  <div
                    className="h-full rounded-full"
                    style={{
                      width: `${weightPct}%`,
                      backgroundColor: display.color,
                    }}
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Ensemble temperature */}
      <div className="mt-4 rounded-lg bg-slate-800/60 p-3 text-center">
        <div className="text-xs text-slate-400 mb-0.5">Ensemble fused temperature</div>
        <div className="text-2xl font-semibold text-slate-100">
          {Math.round(ensemble.temperature_2m)}°C
        </div>
      </div>
    </div>
  );
}
