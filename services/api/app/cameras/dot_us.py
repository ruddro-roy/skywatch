"""
US DOT 511 / UDOT Traffic Camera source.

Legal basis: 23 U.S.C. § 154 — US federal highway data is public domain.
State-level DOT camera feeds are generally public domain for informational use.

This module provides one working example: Utah DOT (UDOT).
UDOT Traffic API: https://api.udottraffic.utah.gov/v1/
Documentation: https://udottraffic.utah.gov/developer

TODO: Add additional state 511 feeds:
- Georgia: https://511ga.org/api/v2/
- California: https://cwwp2.dot.ca.gov/documentation/cctv/cctv.htm
- Oregon: https://api.tripcheck.com/docs
- Washington: https://wsdot.wa.gov/traffic/api/

Note: This source only has cameras in Utah, USA.
For a global deployment, Windy Webcams API provides better coverage.
"""

import logging
import math

import httpx

from app.cameras.base import CameraSource, RawCamera
from app.config import settings

logger = logging.getLogger(__name__)

_UDOT_API_BASE = "https://api.udottraffic.utah.gov/v1"


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points in kilometres.

    Uses the haversine formula.
    """
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


class USDotCameraSource(CameraSource):
    """
    US DOT 511 camera source — UDOT example.

    Returns public-domain traffic cameras from Utah DOT.
    No API key required. Only covers Utah, USA.
    """

    @property
    def name(self) -> str:
        return "dot_us"

    async def fetch_cameras(
        self, lat: float, lon: float, radius_km: float, limit: int = 8
    ) -> list[RawCamera]:
        """
        Fetch UDOT cameras near the given coordinates.

        Only relevant for queries near Utah, USA (lat 37–42, lon -114 to -109).
        Returns empty list if the query is far outside Utah's bounding box.
        """
        # Quick bounding box check — avoid querying UDOT for non-Utah locations
        # Utah bounding box: lat 36.9–42.0, lon -114.1 to -109.0
        if not (35.0 <= lat <= 43.0 and -115.0 <= lon <= -108.0):
            logger.debug("Query outside Utah — skipping UDOT source")
            return []

        url = f"{_UDOT_API_BASE}/CCTVs"
        params = {
            "format": "json",
        }

        try:
            async with httpx.AsyncClient(timeout=settings.camera_timeout_s) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

            cameras: list[RawCamera] = []
            items = data if isinstance(data, list) else data.get("CCTVs", [])

            for cam in items:
                try:
                    cam_lat = float(cam.get("Latitude") or cam.get("latitude", 0))
                    cam_lon = float(cam.get("Longitude") or cam.get("longitude", 0))

                    if cam_lat == 0 and cam_lon == 0:
                        continue

                    dist = _haversine_km(lat, lon, cam_lat, cam_lon)
                    if dist > radius_km:
                        continue

                    cam_id = str(cam.get("CctvId") or cam.get("id", ""))
                    name = cam.get("Location") or cam.get("name", f"UDOT Camera {cam_id}")

                    # UDOT provides a snapshot URL
                    thumbnail_url = cam.get("ImageUrl") or cam.get("imageUrl")

                    cameras.append(
                        RawCamera(
                            id=f"udot_{cam_id}",
                            source=self.name,
                            name=name,
                            lat=cam_lat,
                            lon=cam_lon,
                            thumbnail_url=thumbnail_url,
                            attribution_url="https://udottraffic.utah.gov/",
                        )
                    )
                except (TypeError, ValueError, KeyError):
                    continue

            # Sort by distance and cap at limit
            cameras.sort(key=lambda c: _haversine_km(lat, lon, c.lat, c.lon))
            cameras = cameras[:limit]

            logger.info("UDOT: found %d cameras within %dkm", len(cameras), radius_km)
            return cameras

        except httpx.TimeoutException:
            logger.warning("UDOT API request timed out")
            return []
        except Exception:
            logger.debug("UDOT API unavailable or parse error — skipping")
            return []
