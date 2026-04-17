"""
skywatch IP geolocation module.

Privacy guarantee:
- The IP address is NEVER logged, stored, or returned in any response
- It is used once to query ipapi.co for city-level location
- The resolved city-level data is returned; the IP is discarded
- If geolocation fails for any reason, None is returned gracefully
"""

import logging
from typing import Optional

import httpx

from app.config import settings
from app.schemas import GeoIPResponse

logger = logging.getLogger(__name__)


async def resolve_ip_to_location(ip: str) -> Optional[GeoIPResponse]:
    """
    Resolve an IP address to a city-level location.

    Uses ipapi.co (free tier: 1,000 req/day without key, 30,000/month with key).
    The IP is sent to ipapi.co only and discarded immediately after.

    Args:
        ip: The client IP address. NEVER log this value.

    Returns:
        GeoIPResponse with city-level location, or None if lookup fails.
    """
    if not ip or ip in ("", "127.0.0.1", "::1", "localhost"):
        logger.debug("Geolocation skipped for local/empty IP")
        return None

    # Build URL — use token if available for higher rate limits
    if settings.ipinfo_token:
        url = f"https://ipapi.co/{ip}/json/?key={settings.ipinfo_token}"
    else:
        url = f"https://ipapi.co/{ip}/json/"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

        # ipapi.co error response
        if data.get("error"):
            reason = data.get("reason", "unknown error")
            logger.warning("ipapi.co returned error: %s", reason)
            return None

        lat = data.get("latitude")
        lon = data.get("longitude")

        if lat is None or lon is None:
            logger.warning("ipapi.co response missing lat/lon")
            return None

        return GeoIPResponse(
            city=data.get("city") or "Unknown",
            country=data.get("country_name") or "Unknown",
            country_code=data.get("country_code"),
            region=data.get("region"),
            lat=float(lat),
            lon=float(lon),
        )

    except httpx.TimeoutException:
        logger.warning("ipapi.co request timed out")
        return None
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 429:
            logger.warning("ipapi.co rate limit reached (free tier exhausted)")
        else:
            logger.warning("ipapi.co HTTP error: %s", exc.response.status_code)
        return None
    except Exception:
        # Never log the IP address in error messages
        logger.warning("Geolocation lookup failed (details omitted for privacy)")
        return None
