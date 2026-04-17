# skywatch

A small weather prototype that pulls a forecast from Open-Meteo and can layer in computer-vision checks against public webcams when keys are provided. Privacy is a design goal: no browser Geolocation API, no IP logging.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org)

First demo: [live page](https://ruddro-roy.github.io/skywatch/) · [DEMO.md](DEMO.md). Captured April 17, 2026.

## What it does today

- Pulls a 7-day forecast from Open-Meteo (ECMWF IFS), no API key needed.
- Resolves the user's city from server-side IP via ipapi.co and discards the IP.
- Has a manual city picker using Open-Meteo's geocoding API.
- Renders a dashboard with current conditions, a 7-day chart, and a camera grid.
- Runs an HSV + Sobel heuristic on webcam frames as a basic cloud/clear check.
- Has stub integrations for OpenWeatherMap, Windy webcams, and NVIDIA Earth-2 NIM that activate when keys are set.

The ensemble layer works with a single active provider. It does not do anything clever with just one model; it becomes useful once more providers are keyed in.

## Quickstart

```bash
git clone https://github.com/ruddro-roy/skywatch.git
cd skywatch
cp .env.example .env
docker-compose up --build
# open http://localhost:3000
```

No API keys are required to get the forecast and the dashboard running. Open-Meteo and ipapi.co have free tiers with no registration.

### Without Docker

```bash
# Backend
cd services/api
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd apps/web
npm install
npm run dev
```

## Status

| Feature | State |
|---|---|
| Open-Meteo 7-day forecast | Working, no key |
| IP to city geolocation (ipapi.co) | Working, no key |
| Manual city picker | Working |
| Ensemble fusion | Working with 1 provider; more interesting with more |
| OpenWeatherMap provider | Needs `OPENWEATHERMAP_API_KEY`, otherwise returns a stub |
| Windy webcam thumbnails | Needs `WINDY_API_KEY`, otherwise empty list |
| US DOT 511 cameras | State-specific; UDOT example included |
| HSV + Sobel heuristic classifier | Working |
| EfficientNet-B0 classifier | Not trained yet, see `vision/classifier.py` |
| CLIP zero-shot classifier | Not wired yet, see `vision/classifier.py` |
| NVIDIA Earth-2 NIM | Stub, returns mock data |
| Google MetNet | Placeholder, no public API |

## Privacy

- The browser Geolocation API is never called.
- The IP used for city resolution is discarded right after the lookup.
- No cookies, no analytics by default.
- No persistent location storage unless the user opts in.

See [docs/PRIVACY.md](docs/PRIVACY.md).

## Camera sources

Only public, legally-accessible feeds are used. In practice this means the Windy Webcams API (under its terms of service), US DOT 511 state feeds, and NOAA/NWS cameras. Aggregators of unsecured or default-password cameras (Insecam, Opentopia, etc.) are explicitly not used.

See [docs/LEGAL.md](docs/LEGAL.md).

## Contributing

1. Fork and branch from `main`.
2. `cd services/api && pytest`
3. `ruff check .` and `black --check .` for Python.
4. `cd apps/web && npm run lint` for TypeScript.
5. Open a PR with a clear description.

Useful areas to help with:

- Additional forecast providers (see `services/api/app/providers/base.py`).
- Additional camera sources (see `services/api/app/cameras/base.py`).
- Training the weather classifier (see `services/api/app/vision/README.md`).
- Frontend i18n.

## Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md).

## License

MIT, see [LICENSE](LICENSE).

skywatch is an independent open-source project and is not affiliated with any commercial weather provider.
