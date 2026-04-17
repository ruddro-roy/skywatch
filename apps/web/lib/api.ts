/**
 * skywatch API client
 *
 * All requests go to the FastAPI backend.
 * Base URL is configurable via NEXT_PUBLIC_API_BASE_URL.
 */

const API_BASE =
  (typeof window !== "undefined"
    ? process.env.NEXT_PUBLIC_API_BASE_URL
    : process.env.NEXT_PUBLIC_API_BASE_URL) || "http://localhost:8000";

// ─────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────

export interface Location {
  lat: number;
  lon: number;
  city: string;
  country: string;
  country_code?: string;
  region?: string;
}

export interface HourlyForecast {
  time: string; // ISO 8601
  temperature_2m: number;
  precipitation_probability: number;
  precipitation: number;
  wind_speed_10m: number;
  weather_code: number;
}

export interface DailyForecast {
  date: string; // YYYY-MM-DD
  temperature_max: number;
  temperature_min: number;
  precipitation_probability_max: number;
  precipitation_sum: number;
  wind_speed_max: number;
  weather_code: number;
  sunrise: string;
  sunset: string;
}

export interface ProviderResult {
  provider: string;
  weight: number;
  temperature_2m: number;
  weather_code: number;
  available: boolean;
}

export interface WeatherResponse {
  location: Location;
  current: {
    temperature_2m: number;
    apparent_temperature: number;
    relative_humidity_2m: number;
    wind_speed_10m: number;
    wind_direction_10m: number;
    weather_code: number;
    is_day: boolean;
    precipitation: number;
  };
  hourly: HourlyForecast[];
  daily: DailyForecast[];
  ensemble: {
    temperature_2m: number;
    weather_code: number;
    confidence: number;
    std_dev: number;
    provider_results: ProviderResult[];
  };
  providers: string[];
  generated_at: string;
}

export interface CameraResult {
  id: string;
  source: string;
  name: string;
  lat: number;
  lon: number;
  distance_km: number;
  thumbnail_url: string | null;
  attribution_url: string | null;
  condition: {
    label: "clear" | "cloudy" | "fog" | "rain" | "snow" | "unknown";
    confidence: number;
    method: "heuristic" | "efficientnet" | "clip" | "unavailable";
  } | null;
}

export interface CameraResponse {
  cameras: CameraResult[];
  total: number;
  radius_km: number;
}

// ─────────────────────────────────────────────
// Fetch helpers
// ─────────────────────────────────────────────

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const text = await response.text().catch(() => "Unknown error");
    throw new Error(`API error ${response.status}: ${text}`);
  }

  return response.json() as Promise<T>;
}

// ─────────────────────────────────────────────
// Public API functions
// ─────────────────────────────────────────────

/**
 * Resolve current location via server-side IP geolocation.
 * Privacy: IP never leaves the server. Only city-level result returned.
 */
export async function fetchGeoIP(): Promise<Location | null> {
  try {
    const data = await fetch("/api/geoip", {
      cache: "no-store",
    }).then((r) => r.json());

    if (!data || !data.lat || !data.lon) {
      return null;
    }

    return {
      lat: data.lat,
      lon: data.lon,
      city: data.city || "Unknown",
      country: data.country || "Unknown",
      country_code: data.country_code,
      region: data.region,
    };
  } catch {
    return null;
  }
}

/**
 * Fetch fused weather forecast for a lat/lon.
 * Uses the ensemble layer on the backend.
 */
export async function fetchWeather(
  lat: number,
  lon: number
): Promise<WeatherResponse> {
  return apiFetch<WeatherResponse>(
    `/api/weather?lat=${lat.toFixed(4)}&lon=${lon.toFixed(4)}`
  );
}

/**
 * Fetch nearby public webcams with CV-classified conditions.
 */
export async function fetchCameras(
  lat: number,
  lon: number,
  radiusKm = 50
): Promise<CameraResponse> {
  return apiFetch<CameraResponse>(
    `/api/cameras?lat=${lat.toFixed(4)}&lon=${lon.toFixed(4)}&radius=${radiusKm}`
  );
}

/**
 * Search for a city by name using Open-Meteo Geocoding API.
 * Used by LocationPicker — no API key required.
 */
export async function searchCity(query: string): Promise<Location[]> {
  if (!query || query.length < 2) return [];

  const url = `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(query)}&count=10&language=en&format=json`;

  try {
    const response = await fetch(url);
    if (!response.ok) return [];

    const data = await response.json();

    return (data.results || []).map(
      (r: {
        id: number;
        name: string;
        country: string;
        country_code: string;
        admin1: string;
        latitude: number;
        longitude: number;
      }) => ({
        lat: r.latitude,
        lon: r.longitude,
        city: r.name,
        country: r.country,
        country_code: r.country_code,
        region: r.admin1,
      })
    );
  } catch {
    return [];
  }
}

// ─────────────────────────────────────────────
// WMO Weather Code helpers
// ─────────────────────────────────────────────

export function wmoCodeToLabel(code: number): string {
  if (code === 0) return "Clear sky";
  if (code <= 3) return "Partly cloudy";
  if (code <= 9) return "Overcast";
  if (code <= 19) return "Fog";
  if (code <= 29) return "Drizzle";
  if (code <= 39) return "Rain";
  if (code <= 49) return "Fog";
  if (code <= 59) return "Drizzle";
  if (code <= 69) return "Rain";
  if (code <= 79) return "Snow";
  if (code <= 84) return "Rain showers";
  if (code <= 94) return "Snow showers";
  if (code <= 99) return "Thunderstorm";
  return "Unknown";
}

export function wmoCodeToCondition(
  code: number
): "clear" | "cloudy" | "fog" | "rain" | "snow" {
  if (code === 0 || code <= 3) return "clear";
  if (code <= 9) return "cloudy";
  if (code <= 19 || (code >= 40 && code <= 49)) return "fog";
  if (code >= 70 && code <= 79) return "snow";
  if (code >= 85 && code <= 94) return "snow";
  if (code >= 20 && code <= 69) return "rain";
  if (code >= 95) return "rain";
  return "cloudy";
}

export function conditionColor(condition: string): string {
  const colors: Record<string, string> = {
    clear: "text-amber-400",
    cloudy: "text-slate-400",
    fog: "text-slate-300",
    rain: "text-blue-400",
    snow: "text-sky-200",
    unknown: "text-slate-500",
  };
  return colors[condition] ?? colors.unknown;
}
