"use client";

/**
 * ForecastPanel, 7-day chart + daily grid, classic light theme.
 * No emoji, no blue gradient. Neutral palette only.
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
import { wmoCodeToLabel } from "@/lib/api";
import type { WeatherResponse } from "@/lib/api";

interface ForecastPanelProps {
  weather: WeatherResponse | null;
  loading: boolean;
}

function formatDay(dateStr: string): string {
  const d = new Date(dateStr + "T12:00:00Z");
  const today = new Date();
  today.setHours(12, 0, 0, 0);
  if (d.toDateString() === today.toDateString()) return "Today";
  return d.toLocaleDateString("en", { weekday: "short" });
}

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
    <div className="rounded border border-rule bg-paper-raised p-3 font-sans text-xs shadow-sm">
      <p className="mb-1.5 font-medium text-ink">{label}</p>
      {payload.map((entry) => (
        <div key={entry.name} className="flex items-center gap-2">
          <span
            className="h-2 w-2 rounded-full"
            style={{ background: entry.color }}
          />
          <span className="text-ink-mute">{entry.name}:</span>
          <span className="sw-num text-ink">
            {entry.name.includes("Temp")
              ? `${Math.round(entry.value)}°C`
              : `${Math.round(entry.value)}%`}
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
        <div className="skeleton mb-4 h-4 w-32" />
        <div className="skeleton h-48 w-full" />
        <div className="mt-4 grid grid-cols-7 gap-2">
          {Array.from({ length: 7 }).map((_, i) => (
            <div key={i} className="skeleton h-20" />
          ))}
        </div>
      </div>
    );
  }

  if (!weather?.daily?.length) {
    return (
      <div className="sw-card flex items-center justify-center py-16 font-sans text-sm text-ink-mute">
        No forecast data available
      </div>
    );
  }

  const chartData = weather.daily.map((day) => ({
    day: formatDay(day.date),
    "Max Temp": day.temperature_max,
    "Min Temp": day.temperature_min,
    "Precip. Prob.": day.precipitation_probability_max,
  }));

  const TEMP_MAX = "#5a3e1b"; // accent
  const TEMP_MIN = "#8a6a3e"; // accent soft
  const PRECIP = "#c8bfa6"; // neutral panel

  return (
    <div className="sw-card">
      <div className="mb-4 flex items-baseline justify-between gap-3">
        <div className="sw-card-heading">7-day forecast</div>
        <span className="provider-tag">ECMWF IFS via Open-Meteo</span>
      </div>

      <div className="mb-6 h-52 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart
            data={chartData}
            margin={{ top: 5, right: 5, left: -20, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e5ddc9" />
            <XAxis
              dataKey="day"
              tick={{ fontSize: 11, fill: "#5a5a5a" }}
              axisLine={{ stroke: "#c8bfa6" }}
              tickLine={false}
            />
            <YAxis
              yAxisId="temp"
              tick={{ fontSize: 11, fill: "#5a5a5a" }}
              axisLine={false}
              tickLine={false}
              unit="°"
            />
            <YAxis
              yAxisId="precip"
              orientation="right"
              tick={{ fontSize: 11, fill: "#5a5a5a" }}
              axisLine={false}
              tickLine={false}
              unit="%"
              domain={[0, 100]}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{
                fontSize: "11px",
                color: "#5a5a5a",
                paddingTop: "8px",
                fontFamily: "Inter, system-ui, sans-serif",
              }}
            />
            <Bar
              yAxisId="precip"
              dataKey="Precip. Prob."
              fill={PRECIP}
              radius={[2, 2, 0, 0]}
            />
            <Area
              yAxisId="temp"
              dataKey="Max Temp"
              stroke={TEMP_MAX}
              fill={TEMP_MAX}
              fillOpacity={0.1}
              strokeWidth={1.75}
              dot={false}
              activeDot={{ r: 3.5, fill: TEMP_MAX }}
            />
            <Line
              yAxisId="temp"
              dataKey="Min Temp"
              stroke={TEMP_MIN}
              strokeWidth={1.5}
              strokeDasharray="4 3"
              dot={false}
              activeDot={{ r: 3.5, fill: TEMP_MIN }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-4 gap-2 sm:grid-cols-7">
        {weather.daily.map((day) => {
          const label = wmoCodeToLabel(day.weather_code);
          return (
            <div
              key={day.date}
              className="flex flex-col rounded border border-rule bg-paper-panel p-2.5 text-center"
            >
              <span className="font-sans text-xs font-medium text-ink">
                {formatDay(day.date)}
              </span>
              <span
                className="mt-1 font-sans text-xs leading-tight text-ink-mute"
                title={`WMO ${day.weather_code}`}
              >
                {label}
              </span>
              <div className="mt-1.5 flex items-baseline justify-center gap-1.5">
                <span className="sw-num text-sm font-semibold text-ink">
                  {Math.round(day.temperature_max)}°
                </span>
                <span className="sw-num text-xs text-ink-faint">
                  {Math.round(day.temperature_min)}°
                </span>
              </div>
              {day.precipitation_probability_max > 20 && (
                <span className="sw-num mt-1 font-sans text-xs text-ink-mute">
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
