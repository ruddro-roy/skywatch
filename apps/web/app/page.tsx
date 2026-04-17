"use client";

/**
 * skywatch — Main Dashboard Page
 *
 * Privacy decisions made here:
 * - NEVER calls navigator.geolocation — uses server-side IP geolocation only
 * - Location is held in React state (memory) only — never written to localStorage by default
 * - User can override via LocationPicker (manual cascading dropdown)
 */

import { useEffect, useState, useCallback } from "react";
import { LocationPicker } from "@/components/LocationPicker";
import { CurrentConditions } from "@/components/CurrentConditions";
import { ForecastPanel } from "@/components/ForecastPanel";
import { CameraGrid } from "@/components/CameraGrid";
import { EnsembleConfidence } from "@/components/EnsembleConfidence";
import { fetchGeoIP, fetchWeather, fetchCameras } from "@/lib/api";
import type { Location, WeatherResponse, CameraResponse } from "@/lib/api";

// Default demo location — Dhaka, Bangladesh (globally neutral choice)
const DEFAULT_LOCATION: Location = {
  lat: 23.8103,
  lon: 90.4125,
  city: "Dhaka",
  country: "Bangladesh",
};

export default function HomePage() {
  const [location, setLocation] = useState<Location | null>(null);
  const [weather, setWeather] = useState<WeatherResponse | null>(null);
  const [cameras, setCameras] = useState<CameraResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [geolocating, setGeolocating] = useState(true);

  // Step 1: Resolve location via server-side IP geolocation (never GPS)
  useEffect(() => {
    async function resolveLocation() {
      setGeolocating(true);
      try {
        const geoResult = await fetchGeoIP();
        if (geoResult) {
          setLocation(geoResult);
        } else {
          // Fallback to demo default
          setLocation(DEFAULT_LOCATION);
        }
      } catch {
        // Graceful fallback — never crash on geolocation failure
        setLocation(DEFAULT_LOCATION);
      } finally {
        setGeolocating(false);
      }
    }
    resolveLocation();
  }, []);

  // Step 2: Fetch weather + cameras when location is resolved
  const loadData = useCallback(async (loc: Location) => {
    setLoading(true);
    setError(null);
    try {
      const [weatherData, cameraData] = await Promise.all([
        fetchWeather(loc.lat, loc.lon),
        fetchCameras(loc.lat, loc.lon),
      ]);
      setWeather(weatherData);
      setCameras(cameraData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load weather data");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (location) {
      loadData(location);
    }
  }, [location, loadData]);

  const handleLocationChange = (newLocation: Location) => {
    setLocation(newLocation);
  };

  return (
    <div className="min-h-screen">
      {/* Hero / Header */}
      <div className="bg-gradient-to-br from-[#082f49] via-[#0c4a6e] to-[#0369a1] px-4 pt-10 pb-16">
        <div className="mx-auto max-w-7xl">
          {/* Headline */}
          <div className="mb-8 text-center animate-fade-in">
            <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl md:text-5xl">
              Weather, the honest way
            </h1>
            <p className="mt-3 text-base text-sky-200 sm:text-lg max-w-2xl mx-auto">
              Multiple AI models fused into one forecast — verified by real cameras nearby.
              No GPS tracking. No cookies. No compromise.
            </p>
          </div>

          {/* Location bar */}
          <div className="mx-auto max-w-2xl">
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
              <div className="flex items-center gap-2 text-sky-300 text-sm">
                <svg className="h-4 w-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 21s-8-4.5-8-11.8A8 8 0 0 1 12 2a8 8 0 0 1 8 8.2c0 7.3-8 10.8-8 10.8z"/>
                  <circle cx="12" cy="10" r="3"/>
                </svg>
                {geolocating ? (
                  <span className="text-slate-400">Detecting location (city-level, no GPS)…</span>
                ) : (
                  <span>
                    {location?.city}, {location?.country}
                    {" "}
                    <span className="text-sky-500/70 text-xs">(IP-resolved, not stored)</span>
                  </span>
                )}
              </div>
              <div className="sm:ml-auto">
                <LocationPicker
                  currentLocation={location}
                  onLocationChange={handleLocationChange}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Dashboard grid */}
      <div className="mx-auto max-w-7xl px-4 py-8 -mt-8">
        {error && (
          <div className="mb-6 rounded-xl border border-red-700/50 bg-red-900/20 p-4 text-sm text-red-300">
            <strong>Error:</strong> {error}
            {" — "}
            <button
              onClick={() => location && loadData(location)}
              className="underline hover:text-red-200"
            >
              Retry
            </button>
          </div>
        )}

        <div className="grid gap-6 lg:grid-cols-12">
          {/* Current conditions — large card, left */}
          <div className="lg:col-span-4">
            <CurrentConditions
              weather={weather}
              location={location}
              loading={loading || geolocating}
            />
          </div>

          {/* Ensemble confidence */}
          <div className="lg:col-span-8">
            <EnsembleConfidence weather={weather} loading={loading} />
          </div>

          {/* 7-day forecast — full width */}
          <div className="lg:col-span-12">
            <ForecastPanel weather={weather} loading={loading} />
          </div>

          {/* Camera grid — full width */}
          <div className="lg:col-span-12">
            <CameraGrid cameras={cameras} loading={loading} location={location} />
          </div>
        </div>

        {/* Data source attribution */}
        <div className="mt-8 flex flex-wrap gap-3 text-xs text-slate-500">
          <span>Forecast: </span>
          <a href="https://open-meteo.com" target="_blank" rel="noopener noreferrer" className="text-sky-600 hover:text-sky-500">
            Open-Meteo (ECMWF IFS)
          </a>
          {weather?.providers?.map((p) => (
            <span key={p} className="provider-tag">{p}</span>
          ))}
        </div>
      </div>
    </div>
  );
}
