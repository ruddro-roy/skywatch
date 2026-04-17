"""
skywatch weighted ensemble fusion module.

Combines forecasts from multiple providers into a single fused result.
Handles missing/unavailable providers gracefully (minimum 1 active provider).

Fusion algorithm:
    1. Collect results from all providers
    2. Filter to available providers only
    3. Compute weighted mean temperature: Σ(w_i × T_i) / Σ(w_i)
    4. Compute weighted std dev: sqrt(Σ(w_i × (T_i − mean)²) / Σ(w_i))
    5. Normalise confidence: 1 − (std_dev / reference_range)
    6. Mode WMO code across providers (majority vote)

The primary forecast output (hourly, daily, current) comes from the
highest-weight available provider. The ensemble layer adds:
- Fused temperature (weighted mean)
- Confidence score
- Std deviation
- Per-provider breakdown for the UI
"""

import logging
import math
from collections import Counter
from typing import Optional

from app.providers.base import ForecastResult
from app.schemas import EnsembleResult, ProviderResult

logger = logging.getLogger(__name__)

# Reference temperature range for confidence normalisation (°C).
# A spread of 10°C or more → confidence ≈ 0. Adjust as needed.
_REFERENCE_SPREAD_C = 10.0


class WeightedEnsemble:
    """
    Fuses multiple ForecastResult objects into a single EnsembleResult.

    Works with any number of providers ≥ 1. Gracefully handles the
    case where only one provider is active (confidence = 1.0).
    """

    def fuse(self, results: list[ForecastResult]) -> EnsembleResult:
        """
        Compute the weighted ensemble from a list of provider results.

        Args:
            results: List of ForecastResult from all providers (including inactive ones).

        Returns:
            EnsembleResult with fused temperature, confidence, std dev, and
            per-provider breakdown.
        """
        available = [r for r in results if r.available and r.weight > 0]

        if not available:
            logger.error("No available forecast providers — cannot compute ensemble")
            return EnsembleResult(
                temperature_2m=0.0,
                weather_code=0,
                confidence=0.0,
                std_dev=0.0,
                provider_results=self._build_provider_results(results),
            )

        total_weight = sum(r.weight for r in available)

        # Weighted mean temperature
        weighted_mean = sum(r.weight * r.temperature_2m for r in available) / total_weight

        # Weighted variance
        weighted_var = sum(
            r.weight * (r.temperature_2m - weighted_mean) ** 2 for r in available
        ) / total_weight
        std_dev = math.sqrt(weighted_var)

        # Confidence: 1 − normalised spread (clamped 0–1)
        confidence = max(0.0, min(1.0, 1.0 - (std_dev / _REFERENCE_SPREAD_C)))

        # If only one provider is active, confidence is 1.0 by definition
        if len(available) == 1:
            confidence = 1.0

        # Mode WMO code (majority vote, weight-adjusted)
        weather_code = self._mode_weather_code(available)

        return EnsembleResult(
            temperature_2m=round(weighted_mean, 2),
            weather_code=weather_code,
            confidence=round(confidence, 4),
            std_dev=round(std_dev, 2),
            provider_results=self._build_provider_results(results),
        )

    def _mode_weather_code(self, available: list[ForecastResult]) -> int:
        """
        Return the mode WMO weather code weighted by provider weight.

        In practice: highest-weight provider wins ties.
        """
        if not available:
            return 0

        # Weight each provider's code by its weight
        weighted_codes: list[tuple[int, float]] = [
            (r.weather_code, r.weight) for r in available
        ]

        # Aggregate weights per code
        code_weights: dict[int, float] = {}
        for code, weight in weighted_codes:
            code_weights[code] = code_weights.get(code, 0.0) + weight

        # Return the code with highest total weight
        return max(code_weights, key=lambda c: code_weights[c])

    def _build_provider_results(
        self, results: list[ForecastResult]
    ) -> list[ProviderResult]:
        """Build the per-provider breakdown list for the UI."""
        return [
            ProviderResult(
                provider=r.provider,
                weight=r.weight,
                temperature_2m=r.temperature_2m,
                weather_code=r.weather_code,
                available=r.available,
                error=r.error,
            )
            for r in results
        ]

    def primary_result(self, results: list[ForecastResult]) -> Optional[ForecastResult]:
        """
        Return the single provider result to use as the primary forecast
        (i.e., the one from which hourly/daily arrays are taken).

        Picks the available provider with the highest weight.
        """
        available = [r for r in results if r.available and r.weight > 0]
        if not available:
            return None
        return max(available, key=lambda r: r.weight)


# Module-level singleton
ensemble = WeightedEnsemble()
