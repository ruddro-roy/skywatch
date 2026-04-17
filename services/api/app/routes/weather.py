"""
GET /api/weather — Fused forecast endpoint.

Returns real weather data using Open-Meteo as the primary provider,
with the ensemble layer computing confidence across all active providers.
"""

import asyncio
import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.ensemble import ensemble
from app.providers.metnet_stub import MetNetStubProvider
from app.providers.nvidia_earth2 import NvidiaEarth2Provider
from app.providers.open_meteo import OpenMeteoProvider
from app.providers.openweathermap import OpenWeatherMapProvider
from app.schemas import (
    CurrentWeather,
    DailyForecast,
    EnsembleResult,
    HourlyForecast,
    LocationSchema,
    WeatherResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Instantiate providers — add new providers here
_PROVIDERS = [
    OpenMeteoProvider(),
    OpenWeatherMapProvider(),
    NvidiaEarth2Provider(),
    MetNetStubProvider(),
]


@router.get("/weather", response_model=WeatherResponse, tags=["forecast"])
async def get_weather(
    lat: Annotated[float, Query(ge=-90, le=90, description="Latitude")],
    lon: Annotated[float, Query(ge=-180, le=180, description="Longitude")],
) -> WeatherResponse:
    """
    Return a fused weather forecast for the given coordinates.

    - Queries all configured providers in parallel
    - Computes weighted ensemble fusion with confidence intervals
    - Returns current conditions, 7-day hourly, and 7-day daily forecast
    - Always works with at least Open-Meteo (no key required)

    Privacy note: lat/lon are used only for the weather query. They are not
    associated with any user identifier and not written to any log.
    """
    # Query all providers in parallel with individual error handling
    results = await asyncio.gather(
        *[provider.fetch_forecast(lat, lon) for provider in _PROVIDERS],
        return_exceptions=False,
    )

    # Compute ensemble fusion
    ensemble_result: EnsembleResult = ensemble.fuse(list(results))

    # Get primary provider result for hourly/daily arrays
    primary = ensemble.primary_result(list(results))
    if primary is None:
        raise HTTPException(
            status_code=503,
            detail="No forecast providers are currently available. Please try again later.",
        )

    # Build current conditions from primary provider
    current = CurrentWeather(
        temperature_2m=primary.temperature_2m,
        apparent_temperature=primary.apparent_temperature,
        relative_humidity_2m=primary.relative_humidity_2m,
        wind_speed_10m=primary.wind_speed_10m,
        wind_direction_10m=primary.wind_direction_10m,
        weather_code=primary.weather_code,
        is_day=primary.is_day,
        precipitation=primary.precipitation,
    )

    # Parse hourly list
    hourly_forecasts = [HourlyForecast(**h) for h in primary.hourly]

    # Parse daily list
    daily_forecasts = [DailyForecast(**d) for d in primary.daily]

    active_provider_names = [r.provider for r in results if r.available]

    return WeatherResponse(
        location=LocationSchema(
            lat=lat,
            lon=lon,
            city="",  # Filled in by the frontend from GeoIP
            country="",
        ),
        current=current,
        hourly=hourly_forecasts,
        daily=daily_forecasts,
        ensemble=ensemble_result,
        providers=active_provider_names,
    )
