"use client";

/**
 * EnsembleConfidence, provider weights and agreement panel.
 * Classic light theme, no gradients, no slang.
 */

import type { WeatherResponse } from "@/lib/api";

interface EnsembleConfidenceProps {
  weather: WeatherResponse | null;
  loading: boolean;
}

const PROVIDER_DISPLAY: Record<
  string,
  { label: string; url: string }
> = {
  open_meteo: {
    label: "Open-Meteo (ECMWF IFS)",
    url: "https://open-meteo.com",
  },
  openweathermap: {
    label: "OpenWeatherMap (GFS)",
    url: "https://openweathermap.org",
  },
  nvidia_earth2: {
    label: "NVIDIA Earth-2 (FourCastNet)",
    url: "https://docs.api.nvidia.com/nim/reference/nvidia-fourcastnet",
  },
  metnet: {
    label: "Google MetNet-3",
    url: "https://cloud.google.com/blog/topics/developers-practitioners/metnet-3-google-deepminds-weather-model",
  },
};

function Bar({ value, height = 6 }: { value: number; height?: number }) {
  const pct = Math.max(0, Math.min(100, Math.round(value * 100)));
  return (
    <div
      className="relative w-full overflow-hidden rounded-sm bg-paper-panel"
      style={{ height }}
    >
      <div
        className="h-full rounded-sm bg-ink-soft transition-all duration-500"
        style={{ width: `${pct}%` }}
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
        <div className="skeleton mb-3 h-4 w-40" />
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i}>
              <div className="skeleton mb-1.5 h-3 w-32" />
              <div className="skeleton h-2 w-full" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (!weather?.ensemble) {
    return (
      <div className="sw-card flex h-full items-center justify-center font-sans text-sm text-ink-mute">
        No ensemble data
      </div>
    );
  }

  const { ensemble } = weather;
  const confidence = Math.round(ensemble.confidence * 100);
  const activeProviders =
    ensemble.provider_results?.filter((p) => p.available) ?? [];
  const totalWeight = activeProviders.reduce((sum, p) => sum + p.weight, 0);

  return (
    <div className="sw-card h-full">
      <div className="mb-4 flex items-start justify-between gap-6">
        <div>
          <div className="sw-card-heading">Ensemble</div>
          <p className="font-sans text-xs text-ink-mute">
            Weighted agreement across {activeProviders.length} active model
            {activeProviders.length !== 1 ? "s" : ""}
          </p>
        </div>
        <div className="shrink-0 text-right">
          <div className="sw-num text-3xl font-semibold text-ink">
            {confidence}%
          </div>
          <div className="sw-num font-sans text-xs text-ink-mute">
            ±{ensemble.std_dev?.toFixed(1) ?? "—"}°C spread
          </div>
        </div>
      </div>

      <div className="mb-6">
        <Bar value={ensemble.confidence} height={8} />
        <div className="mt-1 flex justify-between font-sans text-xs text-ink-faint">
          <span>Low agreement</span>
          <span>High agreement</span>
        </div>
      </div>

      <div className="space-y-3 border-t border-rule pt-4">
        {ensemble.provider_results?.map((result) => {
          const display =
            PROVIDER_DISPLAY[result.provider] ?? {
              label: result.provider,
              url: "#",
            };
          const weightPct =
            totalWeight > 0
              ? Math.round((result.weight / totalWeight) * 100)
              : 0;

          return (
            <div key={result.provider}>
              <div className="mb-1 flex items-center justify-between gap-3">
                <a
                  href={display.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-sans text-sm text-ink-soft no-underline hover:text-ink"
                >
                  {display.label}
                </a>
                <div className="flex items-center gap-3 font-sans text-xs">
                  {result.available ? (
                    <>
                      <span className="sw-num text-ink-soft">
                        {Math.round(result.temperature_2m)}°C
                      </span>
                      <span className="sw-num text-ink-mute">{weightPct}%</span>
                    </>
                  ) : (
                    <span className="provider-tag">inactive</span>
                  )}
                </div>
              </div>
              {result.available && <Bar value={weightPct / 100} height={4} />}
            </div>
          );
        })}
      </div>

      <div className="mt-5 flex items-baseline justify-between border-t border-rule pt-4">
        <span className="sw-label">Fused temperature</span>
        <span className="sw-num text-2xl font-semibold text-ink">
          {Math.round(ensemble.temperature_2m)}°C
        </span>
      </div>
    </div>
  );
}
