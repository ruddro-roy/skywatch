"""
skywatch FastAPI application entry point.

Registers routes, CORS, and startup events.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import cameras, geoip, weather

# ─────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────

logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("skywatch")

# IMPORTANT: We deliberately do NOT log request IP addresses or query strings
# that could contain location data. See docs/PRIVACY.md for the privacy policy.


# ─────────────────────────────────────────────
# Lifespan
# ─────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup and shutdown events."""
    logger.info("skywatch API starting up (v0.1)")
    logger.info(
        "Active forecast providers: Open-Meteo=always"
        + (", OpenWeatherMap" if settings.openweathermap_api_key else "")
        + (", NVIDIA Earth-2 (stub)" if settings.nvidia_ngc_api_key else "")
    )
    logger.info(
        "Camera sources: Windy=%s, UDOT=enabled",
        "enabled" if settings.windy_api_key else "disabled (no key)",
    )
    yield
    logger.info("skywatch API shutting down")


# ─────────────────────────────────────────────
# App
# ─────────────────────────────────────────────

app = FastAPI(
    title="skywatch API",
    description="Privacy-first hybrid AI weather with computer-vision verification",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS — restrict to configured frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

app.include_router(weather.router, prefix="/api")
app.include_router(cameras.router, prefix="/api")
app.include_router(geoip.router, prefix="/api")


@app.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    """Health check endpoint for Docker and load balancers."""
    return {"status": "ok", "version": "0.1.0"}


@app.get("/", tags=["system"])
async def root() -> dict[str, str]:
    """API root — links to documentation."""
    return {
        "name": "skywatch API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }
