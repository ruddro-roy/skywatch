"use client";

/**
 * CurrentConditions — Current weather card
 *
 * Shows: temperature, apparent temp, humidity, wind, condition label,
 * and a note indicating the condition is CV-verified if camera data is present.
 */

import { wmoCodeToLabel, wmoCodeToCondition } from "@/lib/api";
import type { WeatherResponse, Location } from "@/lib/api";

interface CurrentConditionsProps {
  weather: WeatherResponse | null;
  location: Location | null;
  loading: boolean;
}

const CONDITION_ICONS: Record<string, string> = {
  clear: "☀️",
  cloudy: "☁️",
  fog: "🌫️",
  rain: "🌧️",
  snow: "❄️",
};

const CONDITION_COLORS: Record<string, string> = {
  clear: "from-amber-900/30 to-orange-900/20 border-amber-700/30",
  cloudy: "from-slate-800/60 to-slate-900/40 border-slate-600/30",
  fog: "from-slate-700/40 to-slate-800/30 border-slate-500/30",
  rain: "from-blue-900/40 to-sky-900/30 border-blue-700/30",
  snow: "from-sky-900/30 to-slate-800/30 border-sky-700/30",
};

function WindDirectionLabel(degrees: number): string {
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
      <div className="sw-card h-full min-h-[280px]">
        <div className="skeleton mb-4 h-5 w-40 rounded" />
        <div className="skeleton mb-2 h-16 w-32 rounded" />
        <div className="skeleton mb-4 h-4 w-24 rounded" />
        <div className="mt-4 space-y-2">
          <div className="skeleton h-4 w-full rounded" />
          <div className="skeleton h-4 w-3/4 rounded" />
          <div className="skeleton h-4 w-1/2 rounded" />
        </div>
      </div>
    );
  }

  if (!weather) {
    return (
      <div className="sw-card h-full flex items-center justify-center text-slate-500 text-sm">
        No data
      </div>
    );
  }

  const { current } = weather;
  const condition = wmoCodeToCondition(current.weather_code);
  const conditionLabel = wmoCodeToLabel(current.weather_code);
  const icon = CONDITION_ICONS[condition] ?? "🌡️";
  const colorClass = CONDITION_COLORS[condition] ?? CONDITION_COLORS.cloudy;

  return (
    <div className={`sw-card h-full bg-gradient-to-br ${colorClass} animate-slide-up`}>
      {/* Location */}
      <div className="mb-3 text-sm text-slate-400">
        {location ? (
          <>
            <span className="font-medium text-slate-200">{location.city}</span>
            {location.region && `, ${location.region}`}
            {" · "}
            <span>{location.country}</span>
          </>
        ) : (
          "Current location"
        )}
      </div>

      {/* Main temp */}
      <div className="flex items-end gap-3 mb-1">
        <span className="text-6xl font-light tracking-tight text-white">
          {Math.round(current.temperature_2m)}°
        </span>
        <span className="pb-2 text-4xl">{icon}</span>
      </div>

      {/* Apparent temp */}
      <div className="mb-4 text-sm text-slate-400">
        Feels like {Math.round(current.apparent_temperature)}°C
        {" · "}
        <span className="text-slate-300">{conditionLabel}</span>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 gap-3 text-sm">
        <div className="rounded-lg bg-slate-900/30 p-3">
          <div className="text-xs text-slate-400 mb-1">Humidity</div>
          <div className="font-medium text-slate-100">
            {current.relative_humidity_2m}%
          </div>
        </div>
        <div className="rounded-lg bg-slate-900/30 p-3">
          <div className="text-xs text-slate-400 mb-1">Wind</div>
          <div className="font-medium text-slate-100">
            {Math.round(current.wind_speed_10m)} km/h{" "}
            <span className="text-slate-400 text-xs">
              {WindDirectionLabel(current.wind_direction_10m)}
            </span>
          </div>
        </div>
        {current.precipitation > 0 && (
          <div className="rounded-lg bg-slate-900/30 p-3 col-span-2">
            <div className="text-xs text-slate-400 mb-1">Precipitation</div>
            <div className="font-medium text-slate-100">
              {current.precipitation.toFixed(1)} mm
            </div>
          </div>
        )}
      </div>

      {/* Day/night indicator */}
      <div className="mt-4 text-xs text-slate-500">
        {current.is_day ? "☀️ Daytime" : "🌙 Night"}{" "}
        · WMO code {current.weather_code}
      </div>
    </div>
  );
}
