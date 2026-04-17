"""
Open-Meteo forecast provider — FULLY WORKING.

Free, no API key required. Provides ECMWF IFS-based global forecast.
This is the one provider that always works, making the MVP demo-able.

Docs: https://open-meteo.com/en/docs
License: CC BY 4.0 (non-commercial use free)
"""

import logging
from typing import Any

import httpx

from app.config import settings
from app.providers.base import ForecastProvider, ForecastResult

logger = logging.getLogger(__name__)


class OpenMeteoProvider(ForecastProvider):
    """
    Open-Meteo provider using ECMWF IFS model.

    Fetches current conditions and 7-day hourly/daily forecast.
    No API key required. Works globally.
    """

    @property
    def name(self) -> str:
        return "open_meteo"

    @property
    def default_weight(self) -> float:
        return settings.weight_open_meteo

    async def fetch_forecast(self, lat: float, lon: float) -> ForecastResult:
        """
        Fetch forecast from Open-Meteo API.

        Queries the /forecast endpoint with hourly + daily variables.
        Returns normalised ForecastResult; never raises exceptions.
        """
        url = f"{settings.open_meteo_base_url}/forecast"

        params: dict[str, Any] = {
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            # Current weather variables
            "current": ",".join([
                "temperature_2m",
                "apparent_temperature",
                "relative_humidity_2m",
                "wind_speed_10m",
                "wind_direction_10m",
                "weather_code",
                "is_day",
                "precipitation",
            ]),
            # Hourly variables for 7-day forecast
            "hourly": ",".join([
                "temperature_2m",
                "precipitation_probability",
                "precipitation",
                "wind_speed_10m",
                "weather_code",
            ]),
            # Daily summary variables
            "daily": ",".join([
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_probability_max",
                "precipitation_sum",
                "wind_speed_10m_max",
                "weather_code",
                "sunrise",
                "sunset",
            ]),
            "timezone": "auto",
            "forecast_days": 7,
            "wind_speed_unit": "kmh",
            "temperature_unit": "celsius",
            "precipitation_unit": "mm",
        }

        try:
            async with httpx.AsyncClient(timeout=settings.provider_timeout_s) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

            return self._parse_response(data)

        except httpx.TimeoutException:
            logger.warning("Open-Meteo request timed out for lat=%.4f lon=%.4f", lat, lon)
            return self._error_result("Request timed out")
        except httpx.HTTPStatusError as exc:
            logger.warning("Open-Meteo HTTP error: %s", exc.response.status_code)
            return self._error_result(f"HTTP {exc.response.status_code}")
        except Exception as exc:
            logger.exception("Unexpected error from Open-Meteo")
            return self._error_result(str(exc))

    def _parse_response(self, data: dict) -> ForecastResult:
        """Parse Open-Meteo JSON response into ForecastResult."""
        current = data.get("current", {})
        hourly = data.get("hourly", {})
        daily = data.get("daily", {})

        # Parse hourly data into list of dicts
        hourly_list = []
        times = hourly.get("time", [])
        for i, t in enumerate(times[:168]):  # Cap at 7 days × 24h
            hourly_list.append({
                "time": t,
                "temperature_2m": _safe_float(hourly.get("temperature_2m", [])[i] if i < len(hourly.get("temperature_2m", [])) else None, 0.0),
                "precipitation_probability": _safe_int(hourly.get("precipitation_probability", [])[i] if i < len(hourly.get("precipitation_probability", [])) else None, 0),
                "precipitation": _safe_float(hourly.get("precipitation", [])[i] if i < len(hourly.get("precipitation", [])) else None, 0.0),
                "wind_speed_10m": _safe_float(hourly.get("wind_speed_10m", [])[i] if i < len(hourly.get("wind_speed_10m", [])) else None, 0.0),
                "weather_code": _safe_int(hourly.get("weather_code", [])[i] if i < len(hourly.get("weather_code", [])) else None, 0),
            })

        # Parse daily data into list of dicts
        daily_list = []
        dates = daily.get("time", [])
        for i, d in enumerate(dates[:7]):
            daily_list.append({
                "date": d,
                "temperature_max": _safe_float(daily.get("temperature_2m_max", [])[i] if i < len(daily.get("temperature_2m_max", [])) else None, 0.0),
                "temperature_min": _safe_float(daily.get("temperature_2m_min", [])[i] if i < len(daily.get("temperature_2m_min", [])) else None, 0.0),
                "precipitation_probability_max": _safe_int(daily.get("precipitation_probability_max", [])[i] if i < len(daily.get("precipitation_probability_max", [])) else None, 0),
                "precipitation_sum": _safe_float(daily.get("precipitation_sum", [])[i] if i < len(daily.get("precipitation_sum", [])) else None, 0.0),
                "wind_speed_max": _safe_float(daily.get("wind_speed_10m_max", [])[i] if i < len(daily.get("wind_speed_10m_max", [])) else None, 0.0),
                "weather_code": _safe_int(daily.get("weather_code", [])[i] if i < len(daily.get("weather_code", [])) else None, 0),
                "sunrise": daily.get("sunrise", [])[i] if i < len(daily.get("sunrise", [])) else "",
                "sunset": daily.get("sunset", [])[i] if i < len(daily.get("sunset", [])) else "",
            })

        return ForecastResult(
            provider=self.name,
            weight=self.default_weight,
            temperature_2m=_safe_float(current.get("temperature_2m"), 0.0),
            apparent_temperature=_safe_float(current.get("apparent_temperature"), 0.0),
            relative_humidity_2m=_safe_int(current.get("relative_humidity_2m"), 50),
            wind_speed_10m=_safe_float(current.get("wind_speed_10m"), 0.0),
            wind_direction_10m=_safe_int(current.get("wind_direction_10m"), 0),
            weather_code=_safe_int(current.get("weather_code"), 0),
            is_day=bool(current.get("is_day", 1)),
            precipitation=_safe_float(current.get("precipitation"), 0.0),
            hourly=hourly_list,
            daily=daily_list,
            available=True,
        )

    def _error_result(self, error: str) -> ForecastResult:
        """Return a disabled provider result with an error message."""
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


def _safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert a value to float, returning default if None or invalid."""
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    """Safely convert a value to int, returning default if None or invalid."""
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
