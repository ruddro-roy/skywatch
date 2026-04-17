"""
Windy Webcams API v3 source.

Status: Working if WINDY_API_KEY is configured; returns empty list otherwise.

Legal basis: Windy Webcams API ToS — https://api.windy.com/webcams/docs#terms
Required attribution: "Weather camera provided by Windy.com"
Free tier: 500 calls/day

Docs: https://api.windy.com/webcams/docs
API endpoint: https://api.windy.com/api/webcams/v3/webcams
"""

import logging

import httpx

from app.cameras.base import CameraSource, RawCamera
from app.config import settings

logger = logging.getLogger(__name__)

_WINDY_API_BASE = "https://api.windy.com/api/webcams/v3"


class WindyCameraSource(CameraSource):
    """
    Windy Webcams API v3 source.

    Returns ToS-compliant camera thumbnails with proper attribution.
    Requires WINDY_API_KEY — returns empty list without it.
    """

    @property
    def name(self) -> str:
        return "windy"

    async def fetch_cameras(
        self, lat: float, lon: float, radius_km: float, limit: int = 8
    ) -> list[RawCamera]:
        """
        Fetch nearby cameras from Windy Webcams API.

        Uses the /webcams endpoint with lat/lon/radius search.
        Returns thumbnail URLs that can be displayed with attribution.
        """
        if not settings.windy_api_key:
            logger.debug("Windy camera source disabled — no API key configured")
            return []

        url = f"{_WINDY_API_BASE}/webcams"
        params = {
            "lat": round(lat, 4),
            "lon": round(lon, 4),
            "radius": int(radius_km),
            "limit": min(limit, 50),  # API cap
            "offset": 0,
            # Request image thumbnails + category
            "include": "images,location,categories",
        }
        headers = {
            "x-windy-api-key": settings.windy_api_key,
            "Accept": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=settings.camera_timeout_s) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()

            cameras: list[RawCamera] = []
            for cam in data.get("webcams", []):
                cam_id = str(cam.get("webcamId", cam.get("id", "")))
                title = cam.get("title", "Windy Camera")

                location = cam.get("location", {})
                cam_lat = float(location.get("latitude", lat))
                cam_lon = float(location.get("longitude", lon))

                # Get the best available thumbnail
                images = cam.get("images", {})
                thumbnail_url = (
                    images.get("current", {}).get("preview")
                    or images.get("current", {}).get("icon")
                )

                cameras.append(
                    RawCamera(
                        id=f"windy_{cam_id}",
                        source=self.name,
                        name=title,
                        lat=cam_lat,
                        lon=cam_lon,
                        thumbnail_url=thumbnail_url,
                        # Windy ToS requires link back to the camera page
                        attribution_url=f"https://www.windy.com/webcams/{cam_id}",
                    )
                )

            logger.info("Windy: found %d cameras within %dkm", len(cameras), radius_km)
            return cameras

        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 401:
                logger.warning("Windy API key invalid or expired")
            elif exc.response.status_code == 429:
                logger.warning("Windy API rate limit reached")
            else:
                logger.warning("Windy API HTTP error: %s", exc.response.status_code)
            return []
        except httpx.TimeoutException:
            logger.warning("Windy API request timed out")
            return []
        except Exception:
            logger.exception("Unexpected error fetching Windy cameras")
            return []
