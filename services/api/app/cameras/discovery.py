"""
Camera discovery — aggregates all sources and applies CV classification.

Given a lat/lon and radius, queries all registered camera sources in parallel,
deduplicates results, runs the CV classifier on each thumbnail, and returns
a sorted list of CameraResult objects.
"""

import asyncio
import logging
import math
from typing import Optional

import httpx

from app.cameras.base import CameraSource, RawCamera
from app.cameras.dot_us import USDotCameraSource
from app.cameras.windy import WindyCameraSource
from app.config import settings
from app.schemas import CameraResult, ConditionResult, CVMethod, WeatherConditionLabel
from app.vision.classifier import WeatherClassifier

logger = logging.getLogger(__name__)

# Classifier singleton — initialised once
_classifier = WeatherClassifier()


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in kilometres."""
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return 2 * r * math.asin(math.sqrt(a))


async def _fetch_thumbnail_bytes(url: str) -> Optional[bytes]:
    """Fetch image bytes from a URL. Returns None on any error."""
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url, follow_redirects=True)
            resp.raise_for_status()
            content_type = resp.headers.get("content-type", "")
            if "image" in content_type or len(resp.content) > 1000:
                return resp.content
    except Exception:
        pass
    return None


async def _classify_camera(cam: RawCamera, origin_lat: float, origin_lon: float) -> CameraResult:
    """Fetch thumbnail and classify condition for a single camera."""
    distance_km = _haversine_km(origin_lat, origin_lon, cam.lat, cam.lon)

    condition: Optional[ConditionResult] = None

    if cam.thumbnail_url:
        image_bytes = await _fetch_thumbnail_bytes(cam.thumbnail_url)
        if image_bytes:
            try:
                label, confidence, method = await asyncio.to_thread(
                    _classifier.classify, image_bytes
                )
                condition = ConditionResult(
                    label=WeatherConditionLabel(label),
                    confidence=confidence,
                    method=CVMethod(method),
                )
            except Exception as exc:
                logger.debug("CV classification failed for %s: %s", cam.id, exc)
                condition = ConditionResult(
                    label=WeatherConditionLabel.UNKNOWN,
                    confidence=0.0,
                    method=CVMethod.UNAVAILABLE,
                )
        else:
            condition = ConditionResult(
                label=WeatherConditionLabel.UNKNOWN,
                confidence=0.0,
                method=CVMethod.UNAVAILABLE,
            )

    return CameraResult(
        id=cam.id,
        source=cam.source,
        name=cam.name,
        lat=cam.lat,
        lon=cam.lon,
        distance_km=round(distance_km, 2),
        thumbnail_url=cam.thumbnail_url,
        attribution_url=cam.attribution_url,
        condition=condition,
    )


class CameraDiscovery:
    """
    Aggregates cameras from all registered sources and classifies them.

    Sources are queried in parallel. Results are sorted by distance.
    """

    def __init__(self) -> None:
        self._sources: list[CameraSource] = [
            WindyCameraSource(),
            USDotCameraSource(),
            # TODO: Add more sources as they become available:
            # NOAACamera Source(),
            # TfLCameraSource(),
            # TransportNSWCameraSource(),
        ]

    async def find_nearby(
        self, lat: float, lon: float, radius_km: float
    ) -> list[CameraResult]:
        """
        Find and classify cameras near the given coordinates.

        Queries all sources in parallel, deduplicates by ID, runs CV
        classification on each thumbnail, and returns sorted results.
        """
        per_source_limit = settings.max_cameras_per_source

        # Query all sources in parallel
        source_results = await asyncio.gather(
            *[
                source.fetch_cameras(lat, lon, radius_km, per_source_limit)
                for source in self._sources
            ],
            return_exceptions=True,
        )

        # Flatten and deduplicate
        all_cameras: list[RawCamera] = []
        seen_ids: set[str] = set()

        for result in source_results:
            if isinstance(result, Exception):
                logger.warning("Camera source error: %s", result)
                continue
            for cam in result:
                if cam.id not in seen_ids:
                    seen_ids.add(cam.id)
                    all_cameras.append(cam)

        if not all_cameras:
            return []

        # Sort by distance before classifying (prioritise closest cameras)
        all_cameras.sort(
            key=lambda c: _haversine_km(lat, lon, c.lat, c.lon)
        )

        # Classify all cameras in parallel (thumbnail fetch + CV)
        classified = await asyncio.gather(
            *[_classify_camera(cam, lat, lon) for cam in all_cameras],
            return_exceptions=True,
        )

        results: list[CameraResult] = []
        for item in classified:
            if isinstance(item, CameraResult):
                results.append(item)

        # Sort by distance ascending
        results.sort(key=lambda c: c.distance_km)

        return results
