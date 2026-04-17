"""
NVIDIA Earth-2 / FourCastNet NIM provider — STUB (v0.1).

Status: Returns mock data. Full integration is v0.3.

TODO (v0.3):
1. Obtain initial atmospheric conditions:
   - ERA5 reanalysis via CDS API (https://cds.climate.copernicus.eu) for hindcasts
   - GFS analysis from NOAA NOMADS (https://nomads.ncep.noaa.gov) for real-time
2. Format as required by NIM input schema (see docs below)
3. Call the NIM endpoint at NVIDIA_NIM_BASE_URL
4. Parse the 73-variable FourCastNet output
5. Map variables to ForecastResult fields

NIM docs: https://docs.api.nvidia.com/nim/reference/nvidia-fourcastnet
NIM API base: https://integrate.api.nvidia.com/v1
Authentication: NGC API key via Authorization: Bearer header

Example request (placeholder — verify against live NIM docs):
    POST /v1/chat/completions  →  (NIM uses a completion-style envelope)

FourCastNet output variables include:
    - u10m, v10m (10m wind components)
    - t2m (2m temperature)
    - sp (surface pressure)
    - msl (mean sea level pressure)
    - tcwv (total column water vapour)
    - tp (total precipitation)
    ... (73 variables total at 0.25° global resolution)
"""

import logging

from app.config import settings
from app.providers.base import ForecastProvider, ForecastResult

logger = logging.getLogger(__name__)


class NvidiaEarth2Provider(ForecastProvider):
    """
    NVIDIA Earth-2 / FourCastNet NIM provider.

    MVP: Returns mock data with a clear warning in the log.
    v0.3: Full integration with real initial conditions.
    """

    @property
    def name(self) -> str:
        return "nvidia_earth2"

    @property
    def default_weight(self) -> float:
        # Only gets non-zero weight when key is present
        # Even then, it's a stub in v0.1 — weight is intentionally low
        return 0.3 if settings.nvidia_ngc_api_key else 0.0

    async def fetch_forecast(self, lat: float, lon: float) -> ForecastResult:
        """
        TODO (v0.3): Implement real Earth-2 NIM inference.

        Steps to implement:
        1. Download GFS analysis GRIB2 file from NOMADS:
           URL: https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/
        2. Extract the 73 FourCastNet input variables at the nearest grid point
        3. POST to NIM endpoint with the initial condition tensor
        4. Poll for result or receive streaming response
        5. Extract forecast values for the target lat/lon
        6. Map to ForecastResult

        For now, returns a clearly-labelled mock result.
        """
        if not settings.nvidia_ngc_api_key:
            logger.debug("NVIDIA Earth-2 disabled — no NGC API key configured")
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
                error="Set NVIDIA_NGC_API_KEY in .env to enable Earth-2 NIM",
            )

        # TODO (v0.3): Replace this mock with real NIM inference
        logger.warning(
            "NVIDIA Earth-2 provider is a stub — returning mock data. "
            "Set NVIDIA_NGC_API_KEY and implement fetch_forecast() for real inference."
        )
        return ForecastResult(
            provider=self.name,
            weight=self.default_weight,
            # Mock: slightly different from Open-Meteo to show ensemble spread
            temperature_2m=0.0,  # TODO: replace with real NIM output
            apparent_temperature=0.0,
            relative_humidity_2m=50,
            wind_speed_10m=0.0,
            wind_direction_10m=0,
            weather_code=0,
            is_day=True,
            available=False,  # Keep False until real integration
            error="NIM integration pending (v0.3) — see services/api/app/providers/nvidia_earth2.py",
        )
