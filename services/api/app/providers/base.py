"""
Abstract base class for all forecast providers.

To add a new provider:
1. Create a new file in this directory (e.g., my_provider.py)
2. Subclass ForecastProvider
3. Implement fetch_forecast()
4. Register in app/providers/__init__.py
5. Instantiate in app/routes/weather.py
6. Document in docs/PROVIDERS.md
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ForecastResult:
    """
    Normalised single-point forecast from any provider.

    All providers must map their raw output to this schema before
    returning. Temperature in Celsius, wind in km/h, precipitation in mm.
    """

    provider: str
    weight: float

    # Current conditions
    temperature_2m: float
    apparent_temperature: float
    relative_humidity_2m: int
    wind_speed_10m: float
    wind_direction_10m: int
    weather_code: int  # WMO weather interpretation code
    is_day: bool
    precipitation: float = 0.0

    # Hourly forecast (list of dicts matching HourlyForecast schema)
    hourly: list[dict] = field(default_factory=list)

    # Daily forecast (list of dicts matching DailyForecast schema)
    daily: list[dict] = field(default_factory=list)

    # Availability flag — set to False if provider is disabled or returned an error
    available: bool = True
    error: Optional[str] = None


class ForecastProvider(abc.ABC):
    """
    Abstract base class for all forecast providers.

    Subclasses must implement `fetch_forecast`.
    The name property must return a stable identifier string.
    """

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Stable identifier for this provider (e.g., 'open_meteo')."""

    @property
    @abc.abstractmethod
    def default_weight(self) -> float:
        """Default ensemble weight. Higher = more influence."""

    @abc.abstractmethod
    async def fetch_forecast(self, lat: float, lon: float) -> ForecastResult:
        """
        Fetch and normalise a forecast for the given coordinates.

        Args:
            lat: Latitude in decimal degrees.
            lon: Longitude in decimal degrees.

        Returns:
            ForecastResult with current + hourly + daily data.
            On error, return a ForecastResult with available=False.
            Never raise exceptions — always return a result.
        """

    async def __call__(self, lat: float, lon: float) -> ForecastResult:
        """Convenience: provider(lat, lon) → ForecastResult."""
        return await self.fetch_forecast(lat, lon)
