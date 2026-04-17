"""
Tests for the weighted ensemble fusion module.

Tests: WeightedEnsemble.fuse() with various provider combinations.
"""

import math

import pytest

from app.ensemble import WeightedEnsemble
from app.providers.base import ForecastResult


def _make_result(
    provider: str,
    temperature: float,
    weight: float = 1.0,
    available: bool = True,
    weather_code: int = 0,
) -> ForecastResult:
    """Helper: construct a ForecastResult with minimal required fields."""
    return ForecastResult(
        provider=provider,
        weight=weight,
        temperature_2m=temperature,
        apparent_temperature=temperature - 2,
        relative_humidity_2m=60,
        wind_speed_10m=10.0,
        wind_direction_10m=180,
        weather_code=weather_code,
        is_day=True,
        available=available,
    )


class TestWeightedEnsembleWithSingleProvider:
    """Single active provider — confidence should be 1.0."""

    def test_single_provider_confidence_is_one(self) -> None:
        ens = WeightedEnsemble()
        results = [_make_result("open_meteo", temperature=25.0, weight=1.0)]
        fused = ens.fuse(results)

        assert fused.confidence == 1.0
        assert fused.temperature_2m == pytest.approx(25.0, abs=0.01)
        assert fused.std_dev == pytest.approx(0.0, abs=0.01)

    def test_single_provider_uses_correct_temperature(self) -> None:
        ens = WeightedEnsemble()
        results = [_make_result("open_meteo", temperature=32.5, weight=1.0)]
        fused = ens.fuse(results)
        assert fused.temperature_2m == pytest.approx(32.5, abs=0.01)


class TestWeightedEnsembleWithMultipleProviders:
    """Multiple providers — weighted average and confidence spread."""

    def test_equal_weights_equal_temps_confidence_is_one(self) -> None:
        ens = WeightedEnsemble()
        results = [
            _make_result("open_meteo", temperature=20.0, weight=1.0),
            _make_result("openweathermap", temperature=20.0, weight=1.0),
        ]
        fused = ens.fuse(results)
        assert fused.confidence == pytest.approx(1.0, abs=0.01)
        assert fused.temperature_2m == pytest.approx(20.0, abs=0.01)
        assert fused.std_dev == pytest.approx(0.0, abs=0.01)

    def test_equal_weights_different_temps_reduces_confidence(self) -> None:
        ens = WeightedEnsemble()
        # 10°C spread should significantly reduce confidence
        results = [
            _make_result("open_meteo", temperature=15.0, weight=1.0),
            _make_result("openweathermap", temperature=25.0, weight=1.0),
        ]
        fused = ens.fuse(results)
        assert fused.confidence < 0.8
        assert fused.temperature_2m == pytest.approx(20.0, abs=0.01)

    def test_weighted_average_favours_higher_weight(self) -> None:
        ens = WeightedEnsemble()
        results = [
            _make_result("open_meteo", temperature=20.0, weight=3.0),  # 75% weight
            _make_result("openweathermap", temperature=28.0, weight=1.0),  # 25% weight
        ]
        fused = ens.fuse(results)
        # Expected: 0.75 * 20 + 0.25 * 28 = 22.0
        assert fused.temperature_2m == pytest.approx(22.0, abs=0.1)

    def test_std_dev_correct(self) -> None:
        ens = WeightedEnsemble()
        results = [
            _make_result("open_meteo", temperature=10.0, weight=1.0),
            _make_result("openweathermap", temperature=20.0, weight=1.0),
        ]
        fused = ens.fuse(results)
        # Weighted mean = 15.0; variance = ((10-15)² + (20-15)²) / 2 = 25; std = 5
        assert fused.std_dev == pytest.approx(5.0, abs=0.01)

    def test_unavailable_providers_are_excluded(self) -> None:
        ens = WeightedEnsemble()
        results = [
            _make_result("open_meteo", temperature=20.0, weight=1.0, available=True),
            _make_result("nvidia_earth2", temperature=999.0, weight=1.0, available=False),
        ]
        fused = ens.fuse(results)
        # Unavailable provider should not affect the result
        assert fused.temperature_2m == pytest.approx(20.0, abs=0.01)
        assert fused.confidence == pytest.approx(1.0, abs=0.01)

    def test_all_unavailable_returns_zero_confidence(self) -> None:
        ens = WeightedEnsemble()
        results = [
            _make_result("p1", temperature=20.0, weight=1.0, available=False),
            _make_result("p2", temperature=20.0, weight=1.0, available=False),
        ]
        fused = ens.fuse(results)
        assert fused.confidence == 0.0

    def test_zero_weight_providers_are_excluded(self) -> None:
        ens = WeightedEnsemble()
        results = [
            _make_result("open_meteo", temperature=20.0, weight=1.0),
            _make_result("metnet", temperature=999.0, weight=0.0, available=True),
        ]
        fused = ens.fuse(results)
        assert fused.temperature_2m == pytest.approx(20.0, abs=0.01)


class TestModeWeatherCode:
    """Ensemble WMO code selection."""

    def test_single_provider_returns_its_code(self) -> None:
        ens = WeightedEnsemble()
        results = [_make_result("open_meteo", temperature=20.0, weather_code=61)]
        fused = ens.fuse(results)
        assert fused.weather_code == 61

    def test_majority_vote_simple(self) -> None:
        ens = WeightedEnsemble()
        results = [
            _make_result("p1", temperature=20.0, weight=1.0, weather_code=0),
            _make_result("p2", temperature=20.0, weight=1.0, weather_code=0),
            _make_result("p3", temperature=20.0, weight=1.0, weather_code=61),
        ]
        fused = ens.fuse(results)
        assert fused.weather_code == 0  # 2 vs 1

    def test_weight_breaks_tie(self) -> None:
        ens = WeightedEnsemble()
        results = [
            _make_result("p1", temperature=20.0, weight=0.5, weather_code=0),
            _make_result("p2", temperature=20.0, weight=2.0, weather_code=61),
        ]
        fused = ens.fuse(results)
        assert fused.weather_code == 61  # Higher weight wins


class TestProviderResults:
    """Ensure per-provider breakdown is correctly included."""

    def test_provider_results_includes_all(self) -> None:
        ens = WeightedEnsemble()
        results = [
            _make_result("open_meteo", temperature=20.0, available=True),
            _make_result("metnet", temperature=0.0, weight=0.0, available=False),
        ]
        fused = ens.fuse(results)
        providers = {p.provider for p in fused.provider_results}
        assert "open_meteo" in providers
        assert "metnet" in providers

    def test_provider_availability_preserved(self) -> None:
        ens = WeightedEnsemble()
        results = [
            _make_result("open_meteo", temperature=20.0, available=True),
            _make_result("metnet", temperature=0.0, weight=0.0, available=False),
        ]
        fused = ens.fuse(results)
        open_meteo = next(p for p in fused.provider_results if p.provider == "open_meteo")
        metnet = next(p for p in fused.provider_results if p.provider == "metnet")
        assert open_meteo.available is True
        assert metnet.available is False
