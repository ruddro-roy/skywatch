"""
OpenWeatherMap forecast provider.

Status: Working if OPENWEATHERMAP_API_KEY is set; returns stub mock otherwise.
Free tier: 1,000 calls/day, 60 calls/minute.
Docs: https://openweathermap.org/api/one-call-3
"""

import logging
from typing import Any

import httpx

from app.config import settings
from app.providers.base import ForecastProvider, ForecastResult

logger = logging.getLogger(__name__)

# WMO code mapping from OWM weather condition IDs
# https://openweathermap.org/weather-conditions
_OWM_ID_TO_WMO = {
    # Thunderstorm
    range(200, 300): 95,
    # Drizzle
    range(300, 400): 51,
    # Rain
    range(500, 511): 61,
    range(511, 512): 77,
    range(511, 600): 80,
    # Snow
    range(600, 700): 71,
    # Atmosphere (fog, mist, haze…)
    range(700, 800): 45,
    # Clear
    range(800, 801): 0,
    # Clouds
    range(801, 803): 2,
    range(803, 900): 3,
}


def _owm_id_to_wmo(owm_id: int) -> int:
    for r, wmo in _OWM_ID_TO_WMO.items():
        if owm_id in r:
            return wmo
    return 0


class OpenWeatherMapProvider(ForecastProvider):
    """
    OpenWeatherMap One Call API 3.0 provider.

    Returns real data if OPENWEATHERMAP_API_KEY is configured.
    Returns a plausible mock if no key is set (so the ensemble still works).
    """

    @property
    def name(self) -> str:
        return "openweathermap"

    @property
    def default_weight(self) -> float:
        return settings.weight_openweathermap if settings.openweathermap_api_key else 0.0

    async def fetch_forecast(self, lat: float, lon: float) -> ForecastResult:
        """Fetch forecast from OpenWeatherMap One Call API."""
        if not settings.openweathermap_api_key:
            logger.debug("OpenWeatherMap disabled — no API key configured")
            return self._stub_result(
                lat=lat,
                lon=lon,
                note="Set OPENWEATHERMAP_API_KEY in .env to enable this provider",
            )

        url = "https://api.openweathermap.org/data/3.0/onecall"
        params = {
            "lat": round(lat, 4),
            "lon": round(lon, 4),
            "exclude": "minutely,alerts",
            "units": "metric",
            "appid": settings.openweathermap_api_key,
        }

        try:
            async with httpx.AsyncClient(timeout=settings.provider_timeout_s) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

            return self._parse_response(data)

        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 401:
                logger.warning("OpenWeatherMap API key invalid or expired")
                return self._error_result("Invalid API key")
            if exc.response.status_code == 429:
                logger.warning("OpenWeatherMap rate limit reached")
                return self._error_result("Rate limit reached")
            logger.warning("OpenWeatherMap HTTP error: %s", exc.response.status_code)
            return self._error_result(f"HTTP {exc.response.status_code}")
        except httpx.TimeoutException:
            logger.warning("OpenWeatherMap request timed out")
            return self._error_result("Request timed out")
        except Exception as exc:
            logger.exception("Unexpected error from OpenWeatherMap")
            return self._error_result(str(exc))

    def _parse_response(self, data: dict[str, Any]) -> ForecastResult:
        """Parse OWM One Call v3 response."""
        current = data.get("current", {})
        weather_list = current.get("weather", [{}])
        owm_id = weather_list[0].get("id", 800) if weather_list else 800
        wmo_code = _owm_id_to_wmo(owm_id)

        hourly_list = []
        for h in data.get("hourly", [])[:48]:
            h_weather = h.get("weather", [{}])
            hourly_list.append({
                "time": _unix_to_iso(h.get("dt", 0)),
                "temperature_2m": float(h.get("temp", 0)),
                "precipitation_probability": int(h.get("pop", 0) * 100),
                "precipitation": float(h.get("rain", {}).get("1h", 0)),
                "wind_speed_10m": float(h.get("wind_speed", 0)) * 3.6,  # m/s → km/h
                "weather_code": _owm_id_to_wmo(
                    h_weather[0].get("id", 800) if h_weather else 800
                ),
            })

        daily_list = []
        for d in data.get("daily", [])[:7]:
            d_weather = d.get("weather", [{}])
            daily_list.append({
                "date": _unix_to_date(d.get("dt", 0)),
                "temperature_max": float(d.get("temp", {}).get("max", 0)),
                "temperature_min": float(d.get("temp", {}).get("min", 0)),
                "precipitation_probability_max": int(d.get("pop", 0) * 100),
                "precipitation_sum": float(d.get("rain", 0)),
                "wind_speed_max": float(d.get("wind_speed", 0)) * 3.6,
                "weather_code": _owm_id_to_wmo(
                    d_weather[0].get("id", 800) if d_weather else 800
                ),
                "sunrise": _unix_to_iso(d.get("sunrise", 0)),
                "sunset": _unix_to_iso(d.get("sunset", 0)),
            })

        return ForecastResult(
            provider=self.name,
            weight=self.default_weight,
            temperature_2m=float(current.get("temp", 0)),
            apparent_temperature=float(current.get("feels_like", 0)),
            relative_humidity_2m=int(current.get("humidity", 50)),
            wind_speed_10m=float(current.get("wind_speed", 0)) * 3.6,
            wind_direction_10m=int(current.get("wind_deg", 0)),
            weather_code=wmo_code,
            is_day=bool(current.get("dt", 0) > current.get("sunrise", 0)),
            precipitation=float(current.get("rain", {}).get("1h", 0)),
            hourly=hourly_list,
            daily=daily_list,
            available=True,
        )

    def _stub_result(self, lat: float, lon: float, note: str) -> ForecastResult:
        """
        Return a stub result when no API key is configured.
        Available=False so the ensemble gives it zero weight.
        """
        return ForecastResult(
            provider=self.name,
            weight=0.0,
            temperature_2m=0.0,
            apparent_temperature=0.0,
            relative_humidity_2m=50,
            wind_speed_10m=0.0,
            wind_direction_10m=0,
            weather_code=0,
            is_day=True,
            available=False,
            error=note,
        )

    def _error_result(self, error: str) -> ForecastResult:
        return ForecastResult(
            provider=self.name,
            weight=0.0,
            temperature_2m=0.0,
            apparent_temperature=0.0,
            relative_humidity_2m=50,
            wind_speed_10m=0.0,
            wind_direction_10m=0,
            weather_code=0,
            is_day=True,
            available=False,
            error=error,
        )


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

from datetime import datetime, timezone


def _unix_to_iso(ts: int) -> str:
    """Convert a Unix timestamp to an ISO 8601 string."""
    try:
        return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
    except Exception:
        return ""


def _unix_to_date(ts: int) -> str:
    """Convert a Unix timestamp to a YYYY-MM-DD date string."""
    try:
        return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
    except Exception:
        return ""
