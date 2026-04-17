"""
Abstract base class for all camera sources.

To add a new camera source:
1. Create a new file in this directory (e.g., tfl.py for Transport for London)
2. Subclass CameraSource
3. Implement fetch_cameras()
4. Register in CameraDiscovery (cameras/discovery.py)
5. Document in docs/PROVIDERS.md
6. Add legal review in docs/LEGAL.md

Legal requirements:
- Every camera source must have a verified legal basis (see docs/LEGAL.md)
- ToS-compliant sources only: Windy API, US DOT 511, NOAA, open-data feeds
- NEVER add Insecam, Opentopia, or any unsecured camera aggregator
"""

from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Optional


@dataclass
class RawCamera:
    """
    Raw camera data from a source, before CV classification.

    The CV classifier is applied by CameraDiscovery after fetching.
    """

    id: str
    source: str
    name: str
    lat: float
    lon: float
    thumbnail_url: Optional[str] = None
    attribution_url: Optional[str] = None


class CameraSource(abc.ABC):
    """Abstract base class for camera sources."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Stable source identifier (e.g., 'windy', 'dot_us')."""

    @abc.abstractmethod
    async def fetch_cameras(
        self, lat: float, lon: float, radius_km: float, limit: int = 8
    ) -> list[RawCamera]:
        """
        Fetch cameras near the given coordinates.

        Args:
            lat: Centre latitude.
            lon: Centre longitude.
            radius_km: Search radius in kilometres.
            limit: Maximum cameras to return.

        Returns:
            List of RawCamera objects. Empty list if source is unavailable
            or returns no results. Never raises exceptions.
        """

    async def __call__(
        self, lat: float, lon: float, radius_km: float, limit: int = 8
    ) -> list[RawCamera]:
        """Convenience: source(lat, lon, radius_km) → cameras."""
        return await self.fetch_cameras(lat, lon, radius_km, limit)
