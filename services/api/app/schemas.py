"""
skywatch Pydantic schemas.

All API request and response types are defined here.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────
# Location
# ─────────────────────────────────────────────


class LocationSchema(BaseModel):
    """Geographic location resolved to city level."""

    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lon: float = Field(..., ge=-180, le=180, description="Longitude")
    city: str = Field(..., description="City name")
    country: str = Field(..., description="Country name")
    country_code: Optional[str] = Field(None, description="ISO 3166-1 alpha-2 code")
    region: Optional[str] = Field(None, description="Administrative region / state")


class GeoIPResponse(BaseModel):
    """Response from the /api/geoip endpoint. Note: IP is never included."""

    city: str
    country: str
    country_code: Optional[str] = None
    region: Optional[str] = None
    lat: float
    lon: float


# ─────────────────────────────────────────────
# Forecast
# ─────────────────────────────────────────────


class HourlyForecast(BaseModel):
    """Single hourly forecast entry."""

    time: str = Field(..., description="ISO 8601 datetime string")
    temperature_2m: float = Field(..., description="Temperature at 2m in °C")
    precipitation_probability: int = Field(..., ge=0, le=100)
    precipitation: float = Field(..., ge=0, description="mm/h")
    wind_speed_10m: float = Field(..., ge=0, description="km/h")
    weather_code: int = Field(..., description="WMO weather interpretation code")


class DailyForecast(BaseModel):
    """Single daily forecast entry."""

    date: str = Field(..., description="YYYY-MM-DD")
    temperature_max: float
    temperature_min: float
    precipitation_probability_max: int = Field(..., ge=0, le=100)
    precipitation_sum: float = Field(..., ge=0)
    wind_speed_max: float = Field(..., ge=0)
    weather_code: int
    sunrise: str = Field(..., description="ISO 8601 datetime")
    sunset: str = Field(..., description="ISO 8601 datetime")


class CurrentWeather(BaseModel):
    """Current weather conditions."""

    temperature_2m: float
    apparent_temperature: float
    relative_humidity_2m: int = Field(..., ge=0, le=100)
    wind_speed_10m: float = Field(..., ge=0)
    wind_direction_10m: int = Field(..., ge=0, le=360)
    weather_code: int
    is_day: bool
    precipitation: float = Field(0.0, ge=0)


class ProviderResult(BaseModel):
    """Result from a single forecast provider, for the ensemble breakdown."""

    provider: str
    weight: float
    temperature_2m: float
    weather_code: int
    available: bool = True
    error: Optional[str] = None


class EnsembleResult(BaseModel):
    """Fused ensemble forecast with confidence metrics."""

    temperature_2m: float = Field(..., description="Weighted mean temperature in °C")
    weather_code: int = Field(..., description="Mode WMO code across providers")
    confidence: float = Field(..., ge=0, le=1, description="Agreement score 0–1")
    std_dev: float = Field(..., ge=0, description="Weighted std dev in °C")
    provider_results: list[ProviderResult] = Field(default_factory=list)


class WeatherResponse(BaseModel):
    """Full weather response from /api/weather."""

    location: LocationSchema
    current: CurrentWeather
    hourly: list[HourlyForecast] = Field(default_factory=list)
    daily: list[DailyForecast] = Field(default_factory=list)
    ensemble: EnsembleResult
    providers: list[str] = Field(default_factory=list, description="Active provider names")
    generated_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z"
    )


# ─────────────────────────────────────────────
# Cameras & CV
# ─────────────────────────────────────────────


class WeatherConditionLabel(str, Enum):
    """CV-detected weather condition labels."""

    CLEAR = "clear"
    CLOUDY = "cloudy"
    FOG = "fog"
    RAIN = "rain"
    SNOW = "snow"
    UNKNOWN = "unknown"


class CVMethod(str, Enum):
    """Method used for condition classification."""

    HEURISTIC = "heuristic"
    EFFICIENTNET = "efficientnet"
    CLIP = "clip"
    UNAVAILABLE = "unavailable"


class ConditionResult(BaseModel):
    """Computer-vision condition detection result."""

    label: WeatherConditionLabel
    confidence: float = Field(..., ge=0, le=1)
    method: CVMethod


class CameraResult(BaseModel):
    """A single webcam result with metadata and CV classification."""

    id: str
    source: str = Field(..., description="Source name: windy, dot_us, noaa, etc.")
    name: str
    lat: float
    lon: float
    distance_km: float
    thumbnail_url: Optional[str] = None
    attribution_url: Optional[str] = None
    condition: Optional[ConditionResult] = None


class CameraResponse(BaseModel):
    """Response from /api/cameras."""

    cameras: list[CameraResult]
    total: int
    radius_km: float
