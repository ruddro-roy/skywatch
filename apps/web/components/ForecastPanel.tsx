"use client";

/**
 * ForecastPanel — 7-day forecast chart + daily grid
 *
 * Uses Recharts for the temperature chart.
 * Shows ensemble fused values with per-model toggle.
 */

import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Area,
} from "recharts";
import { wmoCodeToLabel, wmoCodeToCondition } from "@/lib/api";
import type { WeatherResponse } from "@/lib/api";

interface ForecastPanelProps {
  weather: WeatherResponse | null;
  loading: boolean;
}

// Format ISO date string to short weekday label
function formatDay(dateStr: string): string {
  const d = new Date(dateStr + "T12:00:00Z");
  const today = new Date();
  today.setHours(12, 0, 0, 0);
  if (d.toDateString() === today.toDateString()) return "Today";
  return d.toLocaleDateString("en", { weekday: "short" });
}

const CONDITION_EMOJI: Record<string, string> = {
  clear: "☀️",
  cloudy: "☁️",
  fog: "🌫️",
  rain: "🌧️",
  snow: "❄️",
};

// Custom tooltip for the Recharts chart
function CustomTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: Array<{ value: number; name: string; color: string }>;
  label?: string;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-slate-700 bg-slate-900/95 p-3 text-xs shadow-xl backdrop-blur">
      <p className="mb-2 font-medium text-slate-200">{label}</p>
      {payload.map((entry) => (
        <div key={entry.name} className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full" style={{ background: entry.color }} />
          <span className="text-slate-400">{entry.name}:</span>
          <span className="text-slate-100">
            {entry.name.includes("Temp") ? `${Math.round(entry.value)}°C` : `${Math.round(entry.value)}%`}
          </span>
        </div>
      ))}
    </div>
  );
}

export function ForecastPanel({ weather, loading }: ForecastPanelProps) {
  if (loading) {
    return (
      <div className="sw-card">
        <div className="skeleton mb-4 h-5 w-32 rounded" />
        <div className="skeleton h-48 w-full rounded" />
        <div className="mt-4 grid grid-cols-7 gap-2">
          {Array.from({ length: 7 }).map((_, i) => (
            <div key={i} className="skeleton h-20 rounded" />
          ))}
        </div>
      </div>
    );
  }

  if (!weather?.daily?.length) {
    return (
      <div className="sw-card flex items-center justify-center py-16 text-slate-500 text-sm">
        No forecast data available
      </div>
    );
  }

  // Build chart data from daily forecast
  const chartData = weather.daily.map((day) => ({
    day: formatDay(day.date),
    "Max Temp": day.temperature_max,
    "Min Temp": day.temperature_min,
    "Precip. Prob.": day.precipitation_probability_max,
  }));

  return (
    <div className="sw-card animate-slide-up">
      <h2 className="mb-4 text-sm font-medium text-slate-300">
        7-Day Forecast
        <span className="ml-2 provider-tag">ECMWF IFS via Open-Meteo</span>
      </h2>

      {/* Recharts temperature + precipitation chart */}
      <div className="mb-6 h-52 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis
              dataKey="day"
              tick={{ fontSize: 11, fill: "#94a3b8" }}
              axisLine={{ stroke: "#334155" }}
              tickLine={false}
            />
            <YAxis
              yAxisId="temp"
              tick={{ fontSize: 11, fill: "#94a3b8" }}
              axisLine={false}
              tickLine={false}
              unit="°"
            />
            <YAxis
              yAxisId="precip"
              orientation="right"
              tick={{ fontSize: 11, fill: "#94a3b8" }}
              axisLine={false}
              tickLine={false}
              unit="%"
              domain={[0, 100]}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ fontSize: "11px", color: "#94a3b8", paddingTop: "8px" }}
            />
            {/* Precipitation probability as background bars */}
            <Bar
              yAxisId="precip"
              dataKey="Precip. Prob."
              fill="#1e40af"
              opacity={0.3}
              radius={[2, 2, 0, 0]}
            />
            {/* Temperature range */}
            <Area
              yAxisId="temp"
              dataKey="Max Temp"
              stroke="#f97316"
              fill="#f9731615"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: "#f97316" }}
            />
            <Line
              yAxisId="temp"
              dataKey="Min Temp"
              stroke="#38bdf8"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: "#38bdf8" }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Daily cards */}
      <div className="grid grid-cols-4 gap-2 sm:grid-cols-7">
        {weather.daily.map((day) => {
          const condition = wmoCodeToCondition(day.weather_code);
          const emoji = CONDITION_EMOJI[condition] ?? "🌡️";
          return (
            <div
              key={day.date}
              className="flex flex-col items-center rounded-lg bg-slate-800/50 p-2 text-center hover:bg-slate-700/50 transition-colors"
            >
              <span className="text-xs font-medium text-slate-300 mb-1">
                {formatDay(day.date)}
              </span>
              <span className="text-xl mb-1">{emoji}</span>
              <span className="text-xs text-slate-200">
                {Math.round(day.temperature_max)}°
              </span>
              <span className="text-xs text-slate-500">
                {Math.round(day.temperature_min)}°
              </span>
              {day.precipitation_probability_max > 20 && (
                <span className="mt-1 text-xs text-blue-400">
                  {day.precipitation_probability_max}%
                </span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
