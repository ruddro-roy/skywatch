"""Forecast provider implementations."""

from app.providers.base import ForecastProvider, ForecastResult
from app.providers.open_meteo import OpenMeteoProvider
from app.providers.openweathermap import OpenWeatherMapProvider
from app.providers.nvidia_earth2 import NvidiaEarth2Provider
from app.providers.metnet_stub import MetNetStubProvider

__all__ = [
    "ForecastProvider",
    "ForecastResult",
    "OpenMeteoProvider",
    "OpenWeatherMapProvider",
    "NvidiaEarth2Provider",
    "MetNetStubProvider",
]
