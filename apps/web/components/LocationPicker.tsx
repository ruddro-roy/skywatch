"use client";

/**
 * LocationPicker, cascading city search.
 * Uses Open-Meteo geocoding (free, no key).
 * Never calls navigator.geolocation.
 */

import { useState, useEffect, useRef, useCallback } from "react";
import { searchCity } from "@/lib/api";
import type { Location } from "@/lib/api";

interface LocationPickerProps {
  currentLocation: Location | null;
  onLocationChange: (location: Location) => void;
}

export function LocationPicker({
  currentLocation: _currentLocation,
  onLocationChange,
}: LocationPickerProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Location[]>([]);
  const [open, setOpen] = useState(false);
  const [searching, setSearching] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const doSearch = useCallback(async (q: string) => {
    if (q.length < 2) {
      setResults([]);
      return;
    }
    setSearching(true);
    try {
      const locations = await searchCity(q);
      setResults(locations);
    } finally {
      setSearching(false);
    }
  }, []);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => doSearch(query), 300);
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [query, doSearch]);

  const handleSelect = (loc: Location) => {
    onLocationChange(loc);
    setQuery("");
    setResults([]);
    setOpen(false);
  };

  const containerRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  return (
    <div ref={containerRef} className="relative">
      {!open ? (
        <button
          onClick={() => {
            setOpen(true);
            setTimeout(() => inputRef.current?.focus(), 50);
          }}
          className="inline-flex items-center gap-2 rounded-sm border border-rule bg-paper-raised px-3 py-1.5 font-sans text-sm text-ink-soft hover:border-accentSoft hover:text-ink"
        >
          <svg
            className="h-3.5 w-3.5"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.8"
            aria-hidden="true"
          >
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.35-4.35" />
          </svg>
          Change location
        </button>
      ) : (
        <div className="w-72">
          <div className="relative">
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search city, e.g. Tokyo"
              className="w-full rounded-sm border border-rule bg-paper-raised px-3 py-2 font-sans text-sm text-ink placeholder-ink-faint outline-none focus:border-accent"
              onKeyDown={(e) => {
                if (e.key === "Escape") {
                  setOpen(false);
                  setQuery("");
                }
              }}
            />
            {searching && (
              <div className="absolute right-2.5 top-2.5 h-4 w-4 animate-spin rounded-full border-2 border-accent border-t-transparent" />
            )}
          </div>

          {results.length > 0 && (
            <ul className="absolute z-50 mt-1 max-h-64 w-full overflow-auto rounded-sm border border-rule bg-paper-raised py-1 shadow-sm">
              {results.map((loc, i) => (
                <li key={`${loc.lat}-${loc.lon}-${i}`}>
                  <button
                    onClick={() => handleSelect(loc)}
                    className="flex w-full flex-col px-3 py-2 text-left font-sans hover:bg-paper-panel"
                  >
                    <span className="text-sm font-medium text-ink">
                      {loc.city}
                    </span>
                    <span className="text-xs text-ink-mute">
                      {[loc.region, loc.country].filter(Boolean).join(", ")}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}

          {results.length === 0 && query.length >= 2 && !searching && (
            <div className="absolute z-50 mt-1 w-full rounded-sm border border-rule bg-paper-raised px-3 py-3 font-sans text-sm text-ink-mute shadow-sm">
              No results for &ldquo;{query}&rdquo;
            </div>
          )}

          <button
            onClick={() => {
              setOpen(false);
              setQuery("");
              setResults([]);
            }}
            className="mt-1.5 font-sans text-xs text-ink-faint hover:text-ink-mute"
          >
            Cancel
          </button>
        </div>
      )}
    </div>
  );
}
