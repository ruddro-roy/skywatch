"""
Google MetNet-3 provider — PLACEHOLDER (not yet integrated).

Status: Always returns unavailable. Documentation stub only.

Google MetNet-3 does not have a public REST API as of 2025.
Access requires an enterprise agreement with Google Cloud.

References:
- Research paper: https://arxiv.org/abs/2306.06079
- Blog post: https://cloud.google.com/blog/topics/developers-practitioners/metnet-3-google-deepminds-weather-model
- Google Weather API (future): https://developers.google.com/maps/documentation/weather (preview)

TODO (v0.3+):
- Monitor Google Cloud Weather API status
- When available, implement using Google Cloud credentials
- Add GOOGLE_WEATHER_API_KEY to config.py and .env.example

Why include this now?
The ensemble architecture supports plug-in providers. Including this stub:
1. Documents the intended integration
2. Shows up in the provider breakdown UI with an "inactive" label
3. Makes it easy for a contributor to complete the integration
"""

import logging

from app.providers.base import ForecastProvider, ForecastResult

logger = logging.getLogger(__name__)


class MetNetStubProvider(ForecastProvider):
    """
    Google MetNet-3 placeholder provider.

    Always returns available=False. See module docstring for integration plan.
    """

    @property
    def name(self) -> str:
        return "metnet"

    @property
    def default_weight(self) -> float:
        return 0.0  # Always zero until integrated

    async def fetch_forecast(self, lat: float, lon: float) -> ForecastResult:
        """
        TODO (v0.3+): Implement Google MetNet-3 integration.

        MetNet-3 key features:
        - Up to 24-hour high-resolution forecast (1km resolution)
        - Excels at precipitation nowcasting
        - Trained on ERA5 + HRES ECMWF
        - Direct probability distributions, not deterministic point estimates

        Integration notes when available:
        - Use google-cloud-aiplatform or direct REST API
        - Input: current NWP analysis + recent radar observations
        - Output: precipitation rate, temperature, wind at 1km / 2-min intervals
        """
        logger.debug("MetNet stub provider: always unavailable (v0.3+ integration)")
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
            error="Google MetNet-3 integration pending (v0.3+) — no public API yet",
        )
