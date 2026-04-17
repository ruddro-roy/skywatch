"""
skywatch API configuration.

Loaded from environment variables with sensible defaults.
All API keys are optional — the app degrades gracefully without them.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Server ─────────────────────────────────────────────────────────────
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001"

    # ── Forecast providers ─────────────────────────────────────────────────
    open_meteo_base_url: str = "https://api.open-meteo.com/v1"

    # Optional — set to empty string to disable the provider
    openweathermap_api_key: str = ""
    nvidia_ngc_api_key: str = ""
    nvidia_nim_base_url: str = "https://integrate.api.nvidia.com/v1"

    # ── Geolocation ────────────────────────────────────────────────────────
    # ipapi.co — optional token, works without it up to free-tier limit
    ipinfo_token: str = ""

    # ── Camera sources ─────────────────────────────────────────────────────
    windy_api_key: str = ""

    # ── Ensemble weights ───────────────────────────────────────────────────
    # These are the default relative weights; providers with no key are zeroed out
    weight_open_meteo: float = 1.0
    weight_openweathermap: float = 0.7
    weight_nvidia_earth2: float = 1.2
    weight_metnet: float = 0.9

    # ── Provider timeouts ─────────────────────────────────────────────────
    provider_timeout_s: float = 10.0
    camera_timeout_s: float = 8.0

    # ── Camera discovery ──────────────────────────────────────────────────
    default_camera_radius_km: float = 50.0
    max_cameras_per_source: int = 8

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


# Module-level singleton
settings = Settings()
