"""
GET /api/cameras — Nearby public webcams with CV condition labels.

Queries all configured camera sources in parallel and classifies
each frame using the vision module.
"""

import asyncio
import logging
from typing import Annotated

from fastapi import APIRouter, Query

from app.cameras.discovery import CameraDiscovery
from app.config import settings
from app.schemas import CameraResponse

logger = logging.getLogger(__name__)
router = APIRouter()

_discovery = CameraDiscovery()


@router.get("/cameras", response_model=CameraResponse, tags=["cameras"])
async def get_cameras(
    lat: Annotated[float, Query(ge=-90, le=90, description="Latitude")],
    lon: Annotated[float, Query(ge=-180, le=180, description="Longitude")],
    radius: Annotated[
        float,
        Query(ge=1, le=500, description="Search radius in km"),
    ] = None,
) -> CameraResponse:
    """
    Find nearby public webcams and classify their current conditions.

    - Queries all enabled camera sources in parallel
    - Fetches the latest thumbnail for each camera
    - Runs CV classifier (heuristic HSV + Sobel for MVP) on each frame
    - Returns cameras sorted by distance

    Legal note: Only ToS-compliant sources are queried.
    See docs/LEGAL.md for details.

    Privacy note: lat/lon are used only for the proximity query.
    """
    radius_km = radius or settings.default_camera_radius_km

    cameras = await _discovery.find_nearby(lat=lat, lon=lon, radius_km=radius_km)

    return CameraResponse(
        cameras=cameras,
        total=len(cameras),
        radius_km=radius_km,
    )
