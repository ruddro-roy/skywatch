"""
GET /api/geoip — Ephemeral IP geolocation endpoint.

Privacy guarantee:
- The IP extracted from headers is NEVER logged or returned in the response
- Only city-level data (city, country, region, lat, lon) is returned
- The IP is used solely to make a single lookup and then discarded
"""

import logging

from fastapi import APIRouter, Request

from app.geolocation import resolve_ip_to_location
from app.schemas import GeoIPResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/geoip", response_model=GeoIPResponse, tags=["geolocation"])
async def get_geoip(request: Request) -> GeoIPResponse:
    """
    Resolve the client's IP address to a city-level location.

    The IP is extracted from trusted proxy headers (X-Client-IP or
    X-Forwarded-For set by the Next.js edge route), used once for
    geolocation, and then discarded.

    Returns city, country, region, and approximate lat/lon.
    If geolocation fails, returns a 200 with a default fallback location.

    Privacy:
    - IP is NEVER logged (not even at DEBUG level)
    - IP is NOT included in the response
    - Only city-level data is returned
    """
    # Extract IP from the edge-injected header
    # The Next.js edge route has already sanitised this from the original client IP
    client_ip = (
        request.headers.get("x-client-ip")
        or request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        or (request.client.host if request.client else "")
    )

    location = await resolve_ip_to_location(client_ip)

    if location:
        return location

    # Graceful fallback — return a neutral default
    # The frontend will show the manual location picker
    return GeoIPResponse(
        city="",
        country="",
        country_code=None,
        region=None,
        lat=0.0,
        lon=0.0,
    )
