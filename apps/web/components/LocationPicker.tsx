"use client";

/**
 * LocationPicker — Cascading location search dropdown
 *
 * Uses Open-Meteo Geocoding API (free, no key required) for city search.
 * Privacy: No browser Geolocation API is ever used here.
 * The user explicitly chooses a location via text search.
 */

import { useState, useEffect, useRef, useCallback } from "react";
import { searchCity } from "@/lib/api";
import type { Location } from "@/lib/api";

interface LocationPickerProps {
  currentLocation: Location | null;
  onLocationChange: (location: Location) => void;
}

export function LocationPicker({
  currentLocation,
  onLocationChange,
}: LocationPickerProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Location[]>([]);
  const [open, setOpen] = useState(false);
  const [searching, setSearching] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Debounced search
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

  // Close on outside click
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
          className="flex items-center gap-2 rounded-lg border border-sky-700/50 bg-sky-900/30 px-3 py-1.5 text-sm text-sky-300 hover:bg-sky-800/40 hover:border-sky-600 transition-colors"
        >
          <svg className="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
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
              placeholder="Search city, e.g. Tokyo…"
              className="w-full rounded-lg border border-sky-700/50 bg-slate-900 px-3 py-2 text-sm text-slate-100 placeholder-slate-500 outline-none ring-0 focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
              onKeyDown={(e) => {
                if (e.key === "Escape") {
                  setOpen(false);
                  setQuery("");
                }
              }}
            />
            {searching && (
              <div className="absolute right-2.5 top-2.5">
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-sky-500 border-t-transparent" />
              </div>
            )}
          </div>

          {/* Dropdown results */}
          {results.length > 0 && (
            <ul className="absolute z-50 mt-1 max-h-64 w-full overflow-auto rounded-lg border border-slate-700 bg-slate-900 py-1 shadow-2xl">
              {results.map((loc, i) => (
                <li key={`${loc.lat}-${loc.lon}-${i}`}>
                  <button
                    onClick={() => handleSelect(loc)}
                    className="flex w-full flex-col px-3 py-2 text-left hover:bg-slate-800 transition-colors"
                  >
                    <span className="text-sm font-medium text-slate-100">
                      {loc.city}
                    </span>
                    <span className="text-xs text-slate-400">
                      {[loc.region, loc.country].filter(Boolean).join(", ")}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}

          {results.length === 0 && query.length >= 2 && !searching && (
            <div className="absolute z-50 mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-3 text-sm text-slate-400 shadow-2xl">
              No results for "{query}"
            </div>
          )}

          {/* Cancel */}
          <button
            onClick={() => { setOpen(false); setQuery(""); setResults([]); }}
            className="mt-1.5 text-xs text-slate-500 hover:text-slate-300"
          >
            Cancel
          </button>
        </div>
      )}
    </div>
  );
}
