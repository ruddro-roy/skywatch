"use client";

/**
 * CurrentConditions, current weather card.
 *
 * Shows temperature, apparent temp, humidity, wind, condition label.
 * No emoji. No gradient. No condition icons.
 */

import { wmoCodeToLabel } from "@/lib/api";
import type { WeatherResponse, Location } from "@/lib/api";

interface CurrentConditionsProps {
  weather: WeatherResponse | null;
  location: Location | null;
  loading: boolean;
}

function windDirection(degrees: number): string {
  const dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"];
  return dirs[Math.round(degrees / 45) % 8];
}

export function CurrentConditions({
  weather,
  location,
  loading,
}: CurrentConditionsProps) {
  if (loading) {
    return (
      <div className="sw-card h-full min-h-[260px]">
        <div className="skeleton mb-4 h-4 w-32" />
        <div className="skeleton mb-2 h-14 w-28" />
        <div className="skeleton mb-6 h-4 w-40" />
        <div className="space-y-2">
          <div className="skeleton h-3 w-full" />
          <div className="skeleton h-3 w-3/4" />
        </div>
      </div>
    );
  }

  if (!weather) {
    return (
      <div className="sw-card flex h-full items-center justify-center font-sans text-sm text-ink-mute">
        No data
      </div>
    );
  }

  const { current } = weather;
  const conditionLabel = wmoCodeToLabel(current.weather_code);

  return (
    <div className="sw-card h-full">
      <div className="sw-card-heading">Current conditions</div>

      {/* Temperature */}
      <div className="mb-1 flex items-baseline gap-2">
        <span className="sw-num text-6xl font-light tracking-tight text-ink">
          {Math.round(current.temperature_2m)}
        </span>
        <span className="sw-num text-2xl font-light text-ink-mute">°C</span>
      </div>

      <div className="mb-6 font-sans text-sm text-ink-mute">
        Feels like <span className="sw-num text-ink-soft">{Math.round(current.apparent_temperature)}°C</span>
        <span className="mx-2 text-ink-faint">·</span>
        <span className="text-ink-soft">{conditionLabel}</span>
      </div>

      {/* Stats */}
      <dl className="grid grid-cols-2 gap-4 border-t border-rule pt-4">
        <div>
          <dt className="sw-label">Humidity</dt>
          <dd className="sw-num mt-0.5 text-lg font-medium">{current.relative_humidity_2m}%</dd>
        </div>
        <div>
          <dt className="sw-label">Wind</dt>
          <dd className="sw-num mt-0.5 text-lg font-medium">
            {Math.round(current.wind_speed_10m)}
            <span className="ml-1 text-sm text-ink-mute">km/h {windDirection(current.wind_direction_10m)}</span>
          </dd>
        </div>
        {current.precipitation > 0 && (
          <div className="col-span-2">
            <dt className="sw-label">Precipitation</dt>
            <dd className="sw-num mt-0.5 text-lg font-medium">
              {current.precipitation.toFixed(1)}
              <span className="ml-1 text-sm text-ink-mute">mm</span>
            </dd>
          </div>
        )}
      </dl>

      <div className="mt-4 font-sans text-xs text-ink-faint">
        {current.is_day ? "Daytime" : "Night"}
        <span className="mx-1.5">·</span>
        WMO code {current.weather_code}
        {location && (
          <>
            <span className="mx-1.5">·</span>
            {location.lat.toFixed(2)}°, {location.lon.toFixed(2)}°
          </>
        )}
      </div>
    </div>
  );
}
