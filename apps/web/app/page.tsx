"use client";

/**
 * skywatch, main dashboard page.
 *
 * Privacy notes:
 * - Never calls navigator.geolocation. Uses server-side IP geolocation only.
 * - Location lives in React state only, not persisted to localStorage by default.
 * - User can override via LocationPicker (manual city search).
 */

import { useEffect, useState, useCallback } from "react";
import { LocationPicker } from "@/components/LocationPicker";
import { CurrentConditions } from "@/components/CurrentConditions";
import { ForecastPanel } from "@/components/ForecastPanel";
import { CameraGrid } from "@/components/CameraGrid";
import { EnsembleConfidence } from "@/components/EnsembleConfidence";
import { fetchGeoIP, fetchWeather, fetchCameras } from "@/lib/api";
import type { Location, WeatherResponse, CameraResponse } from "@/lib/api";

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

  useEffect(() => {
    async function resolveLocation() {
      setGeolocating(true);
      try {
        const geoResult = await fetchGeoIP();
        setLocation(geoResult ?? DEFAULT_LOCATION);
      } catch {
        setLocation(DEFAULT_LOCATION);
      } finally {
        setGeolocating(false);
      }
    }
    resolveLocation();
  }, []);

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
    <div className="mx-auto max-w-6xl px-5 pt-8 pb-12">
      {/* Page header, minimal */}
      <div className="mb-8 flex flex-col gap-3 border-b border-rule pb-5 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="font-serif text-3xl font-bold tracking-tight text-ink sm:text-4xl">
            {geolocating ? (
              <span className="text-ink-mute">Detecting location…</span>
            ) : location ? (
              <>{location.city}</>
            ) : (
              "Forecast"
            )}
          </h1>
          <p className="mt-1 font-sans text-sm text-ink-mute">
            {location && !geolocating && (
              <>
                {[location.region, location.country].filter(Boolean).join(", ")}
                <span className="mx-2 text-ink-faint">·</span>
                <span>IP-resolved, not stored</span>
              </>
            )}
          </p>
        </div>
        <LocationPicker
          currentLocation={location}
          onLocationChange={handleLocationChange}
        />
      </div>

      {error && (
        <div className="mb-6 rounded border border-negative/30 bg-paper-panel p-4 font-sans text-sm text-negative">
          <strong>Error.</strong> {error}{" "}
          <button
            onClick={() => location && loadData(location)}
            className="underline hover:no-underline"
          >
            Retry
          </button>
        </div>
      )}

      <div className="grid gap-5 lg:grid-cols-12">
        <div className="lg:col-span-4">
          <CurrentConditions
            weather={weather}
            location={location}
            loading={loading || geolocating}
          />
        </div>

        <div className="lg:col-span-8">
          <EnsembleConfidence weather={weather} loading={loading} />
        </div>

        <div className="lg:col-span-12">
          <ForecastPanel weather={weather} loading={loading} />
        </div>

        <div className="lg:col-span-12">
          <CameraGrid cameras={cameras} loading={loading} location={location} />
        </div>
      </div>

      <div className="mt-8 font-sans text-xs text-ink-faint">
        Forecast:{" "}
        <a href="https://open-meteo.com" target="_blank" rel="noopener noreferrer">
          Open-Meteo (ECMWF IFS)
        </a>
        {weather?.providers && weather.providers.length > 0 && (
          <span className="ml-2">
            {weather.providers.map((p) => (
              <span key={p} className="provider-tag ml-1">
                {p}
              </span>
            ))}
          </span>
        )}
      </div>
    </div>
  );
}
