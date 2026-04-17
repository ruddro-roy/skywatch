"""
Tests for the Open-Meteo forecast provider.

Tests: response parsing, error handling, and real API integration
(integration test is skipped by default — run with --run-integration flag).
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.providers.open_meteo import OpenMeteoProvider, _safe_float, _safe_int


# ─────────────────────────────────────────────
# Sample API response fixture
# ─────────────────────────────────────────────

SAMPLE_OPEN_METEO_RESPONSE = {
    "latitude": 23.8103,
    "longitude": 90.4125,
    "timezone": "Asia/Dhaka",
    "current": {
        "time": "2025-01-15T14:00",
        "temperature_2m": 28.5,
        "apparent_temperature": 31.2,
        "relative_humidity_2m": 72,
        "wind_speed_10m": 12.4,
        "wind_direction_10m": 180,
        "weather_code": 2,
        "is_day": 1,
        "precipitation": 0.0,
    },
    "hourly": {
        "time": [f"2025-01-15T{h:02d}:00" for h in range(24)],
        "temperature_2m": [25.0 + i * 0.2 for i in range(24)],
        "precipitation_probability": [10 + i for i in range(24)],
        "precipitation": [0.0] * 24,
        "wind_speed_10m": [10.0] * 24,
        "weather_code": [2] * 24,
    },
    "daily": {
        "time": [f"2025-01-{15 + i:02d}" for i in range(7)],
        "temperature_2m_max": [30.0 + i for i in range(7)],
        "temperature_2m_min": [22.0 + i for i in range(7)],
        "precipitation_probability_max": [20] * 7,
        "precipitation_sum": [0.0] * 7,
        "wind_speed_10m_max": [15.0] * 7,
        "weather_code": [2] * 7,
        "sunrise": [f"2025-01-{15 + i:02d}T06:00" for i in range(7)],
        "sunset": [f"2025-01-{15 + i:02d}T18:00" for i in range(7)],
    },
}


class TestOpenMeteoProviderMetadata:
    """Provider metadata."""

    def test_name(self) -> None:
        provider = OpenMeteoProvider()
        assert provider.name == "open_meteo"

    def test_default_weight_positive(self) -> None:
        provider = OpenMeteoProvider()
        assert provider.default_weight > 0


class TestOpenMeteoResponseParsing:
    """Test that we correctly parse the Open-Meteo API response format."""

    @pytest.mark.asyncio
    async def test_parses_current_temperature(self) -> None:
        provider = OpenMeteoProvider()
        result = provider._parse_response(SAMPLE_OPEN_METEO_RESPONSE)
        assert result.temperature_2m == pytest.approx(28.5, abs=0.01)

    @pytest.mark.asyncio
    async def test_parses_humidity(self) -> None:
        provider = OpenMeteoProvider()
        result = provider._parse_response(SAMPLE_OPEN_METEO_RESPONSE)
        assert result.relative_humidity_2m == 72

    @pytest.mark.asyncio
    async def test_parses_wind_speed(self) -> None:
        provider = OpenMeteoProvider()
        result = provider._parse_response(SAMPLE_OPEN_METEO_RESPONSE)
        assert result.wind_speed_10m == pytest.approx(12.4, abs=0.01)

    @pytest.mark.asyncio
    async def test_parses_is_day(self) -> None:
        provider = OpenMeteoProvider()
        result = provider._parse_response(SAMPLE_OPEN_METEO_RESPONSE)
        assert result.is_day is True

    @pytest.mark.asyncio
    async def test_parses_7_daily_entries(self) -> None:
        provider = OpenMeteoProvider()
        result = provider._parse_response(SAMPLE_OPEN_METEO_RESPONSE)
        assert len(result.daily) == 7

    @pytest.mark.asyncio
    async def test_parses_daily_temperatures(self) -> None:
        provider = OpenMeteoProvider()
        result = provider._parse_response(SAMPLE_OPEN_METEO_RESPONSE)
        assert result.daily[0]["temperature_max"] == pytest.approx(30.0, abs=0.01)
        assert result.daily[0]["temperature_min"] == pytest.approx(22.0, abs=0.01)

    @pytest.mark.asyncio
    async def test_parses_hourly_entries(self) -> None:
        provider = OpenMeteoProvider()
        result = provider._parse_response(SAMPLE_OPEN_METEO_RESPONSE)
        assert len(result.hourly) == 24

    @pytest.mark.asyncio
    async def test_available_true_on_success(self) -> None:
        provider = OpenMeteoProvider()
        result = provider._parse_response(SAMPLE_OPEN_METEO_RESPONSE)
        assert result.available is True


class TestOpenMeteoErrorHandling:
    """Test error handling — provider never raises, always returns a result."""

    @pytest.mark.asyncio
    async def test_timeout_returns_unavailable(self) -> None:
        import httpx

        provider = OpenMeteoProvider()
        with patch("httpx.AsyncClient") as mock_client:
            mock_cm = AsyncMock()
            mock_cm.__aenter__ = AsyncMock(return_value=mock_cm)
            mock_cm.__aexit__ = AsyncMock(return_value=None)
            mock_cm.get = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
            mock_client.return_value = mock_cm

            result = await provider.fetch_forecast(lat=23.8103, lon=90.4125)

        assert result.available is False
        assert result.weight == 0.0
        assert result.error is not None and len(result.error) > 0

    @pytest.mark.asyncio
    async def test_http_error_returns_unavailable(self) -> None:
        import httpx

        provider = OpenMeteoProvider()
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Server error", request=MagicMock(), response=mock_response
            )

            mock_cm = AsyncMock()
            mock_cm.__aenter__ = AsyncMock(return_value=mock_cm)
            mock_cm.__aexit__ = AsyncMock(return_value=None)
            mock_cm.get = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_cm

            result = await provider.fetch_forecast(lat=23.8103, lon=90.4125)

        assert result.available is False

    @pytest.mark.asyncio
    async def test_empty_response_does_not_raise(self) -> None:
        provider = OpenMeteoProvider()
        # Should not raise even with completely empty response
        result = provider._parse_response({})
        assert result is not None
        assert result.temperature_2m == 0.0


class TestSafeConversions:
    """Test the safe type conversion helpers."""

    def test_safe_float_none_returns_default(self) -> None:
        assert _safe_float(None, 99.0) == 99.0

    def test_safe_float_valid(self) -> None:
        assert _safe_float("28.5") == pytest.approx(28.5)

    def test_safe_float_invalid_string(self) -> None:
        assert _safe_float("not-a-number", -1.0) == -1.0

    def test_safe_int_none_returns_default(self) -> None:
        assert _safe_int(None, 42) == 42

    def test_safe_int_float_input(self) -> None:
        assert _safe_int(3.7) == 3

    def test_safe_int_invalid_string(self) -> None:
        assert _safe_int("abc", 0) == 0


# ─────────────────────────────────────────────
# Integration test — only runs with explicit flag
# Skip by default to avoid network calls in CI
# ─────────────────────────────────────────────

@pytest.mark.skip(reason="Integration test — requires network access. Run with: pytest -k integration")
@pytest.mark.asyncio
async def test_real_open_meteo_dhaka() -> None:
    """
    Integration test: fetch real forecast for Dhaka, Bangladesh.

    Run manually to verify Open-Meteo API is working:
    pytest tests/test_open_meteo.py::test_real_open_meteo_dhaka --no-header -s

    Note: pytest.ini_options sets asyncio_mode = "auto"
    """
    provider = OpenMeteoProvider()
    result = await provider.fetch_forecast(lat=23.8103, lon=90.4125)

    assert result.available is True
    assert -50 <= result.temperature_2m <= 60  # Plausible global range
    assert 0 <= result.relative_humidity_2m <= 100
    assert result.wind_speed_10m >= 0
    assert len(result.daily) == 7
    assert len(result.hourly) > 0
    print(f"\nDhaka current temp: {result.temperature_2m}°C")
    print(f"Condition: WMO code {result.weather_code}")
    print(f"7-day forecast: {[d['temperature_max'] for d in result.daily]}")
