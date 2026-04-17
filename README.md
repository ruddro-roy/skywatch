# skywatch 🌤

**Privacy-first · Hybrid AI · Computer-Vision Verified**

A public open-source weather prototype that fuses multiple AI forecast models with real-time computer-vision verification from legally-accessible public webcams — all without ever touching the browser Geolocation API or storing IP addresses.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![Next.js 15](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org)
[![Open-Meteo](https://img.shields.io/badge/Forecast-Open--Meteo-green.svg)](https://open-meteo.com)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         BROWSER (Next.js 15)                        │
│                                                                     │
│  ┌──────────────────┐  ┌────────────────┐  ┌────────────────────┐  │
│  │  LocationPicker  │  │ CurrentConditions│  │   ForecastPanel   │  │
│  │ (country→region  │  │  (CV-verified) │  │ (ensemble + per-  │  │
│  │    →city drop.)  │  └───────┬────────┘  │   model breakdown)│  │
│  └────────┬─────────┘          │           └────────┬──────────┘  │
│           │                    │                    │              │
│  ┌────────▼────────────────────▼────────────────────▼──────────┐  │
│  │                     lib/api.ts  (httpx client)               │  │
│  └────────────────────────────┬─────────────────────────────────┘  │
└───────────────────────────────│─────────────────────────────────────┘
                                │  REST / JSON
┌───────────────────────────────▼─────────────────────────────────────┐
│                     FastAPI (Python 3.11+)                          │
│                                                                     │
│  ┌────────────────┐  ┌─────────────────┐  ┌────────────────────┐   │
│  │  /api/geoip    │  │  /api/weather   │  │  /api/cameras      │   │
│  │ IP→city ephem. │  │  fused forecast │  │  + CV labels       │   │
│  └───────┬────────┘  └────────┬────────┘  └────────┬───────────┘   │
│          │                    │                    │               │
│  ┌───────▼────────┐  ┌────────▼────────────────────▼───────────┐   │
│  │  geolocation   │  │              ensemble.py                 │   │
│  │  (ipapi.co)    │  │  weighted fusion · confidence · stddev   │   │
│  └────────────────┘  └────────┬──────────────────┬─────────────┘   │
│                               │                  │                 │
│              ┌────────────────▼───┐    ┌─────────▼─────────────┐   │
│              │   providers/       │    │   cameras/            │   │
│              │ ✅ open_meteo      │    │ ☐ windy (key req.)    │   │
│              │ ☐ openweathermap   │    │ ☐ dot_us 511          │   │
│              │ ☐ nvidia_earth2    │    │ ☐ discovery           │   │
│              │ ☐ metnet_stub      │    └─────────┬─────────────┘   │
│              └────────────────────┘              │                 │
│                                        ┌─────────▼─────────────┐   │
│                                        │   vision/classifier   │   │
│                                        │ ✅ HSV heuristic MVP  │   │
│                                        │ ☐ EfficientNet-B0     │   │
│                                        │ ☐ CLIP zero-shot      │   │
│                                        └───────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘

External APIs (all optional except Open-Meteo)
────────────────────────────────────────────────
  Open-Meteo         ── free, no key, global forecast (ECMWF IFS)
  ipapi.co           ── free tier, ephemeral city-level geo
  OpenWeatherMap     ── free 1 000 req/day with API key
  Windy Webcams API  ── cam thumbnails + metadata (key req.)
  NVIDIA NGC NIM     ── Earth-2 / FourCastNet stub (key req.)
  UDOT 511 / 511GA   ── US DOT cameras, public JSON feed
```

---

## Feature Matrix

| Feature | Status | Notes |
|---------|--------|-------|
| Open-Meteo forecast (7-day) | ✅ Working | ECMWF IFS-based, free, global |
| IP → city geolocation | ✅ Working | ipapi.co, ephemeral, never logged |
| Manual location picker | ✅ Working | Country → region → city dropdown |
| Ensemble fusion layer | ✅ Working | Graceful with 1+ providers |
| OpenWeatherMap provider | ⚠️ Key required | Stub returns mock if no key |
| Windy webcam thumbnails | ⚠️ Key required | Stub returns empty list if no key |
| US DOT 511 cameras | ⚠️ State-specific | UDOT example included |
| CV heuristic classifier | ✅ Working | HSV + edge density, no model download |
| EfficientNet-B0 classifier | 🔲 TODO | See vision/classifier.py |
| CLIP zero-shot classifier | 🔲 TODO | See vision/classifier.py |
| NVIDIA Earth-2 NIM | 🔲 Stub | Returns mock data, documents endpoint |
| Google MetNet | 🔲 Stub | Placeholder, requires paid access |

---

## Quickstart (3 commands)

```bash
# 1. Clone and configure
git clone https://github.com/your-org/skywatch.git && cd skywatch
cp .env.example .env   # all keys are optional — works out of the box

# 2. Start everything
docker-compose up --build

# 3. Open browser
open http://localhost:3000
```

> **No API keys required for a working demo.** Open-Meteo and ipapi.co both have generous free tiers with no registration.

### Local development (without Docker)

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

---

## What Works vs What's Stubbed

### ✅ Works on day one (no keys)

- **Open-Meteo forecast**: Full 7-day hourly forecast via ECMWF IFS. Fetched live from `api.open-meteo.com`.
- **IP geolocation**: City-level location via `ipapi.co`. Used only at request time, never persisted.
- **Manual location picker**: Cascading dropdown using Open-Meteo Geocoding API for city search.
- **Ensemble layer**: Weighted fusion works with a single active provider. Returns confidence intervals.
- **CV heuristic classifier**: HSV color analysis + Sobel edge density classifies webcam frames into 5 conditions without any model download.
- **Full frontend**: Dashboard with current conditions, 7-day forecast chart (Recharts), ensemble confidence bar, camera grid.

### ⚠️ Needs API key

- **OpenWeatherMap**: Set `OPENWEATHERMAP_API_KEY` — returns stubbed mock otherwise.
- **Windy Webcams**: Set `WINDY_API_KEY` — returns empty camera list otherwise.
- **NVIDIA Earth-2 NIM**: Set `NVIDIA_NGC_API_KEY` — returns mock forecast otherwise. Full NIM integration is a TODO.

### 🔲 Future work (v0.2+)

- EfficientNet-B0 / MobileNetV3 fine-tuned on FWID dataset
- CLIP zero-shot classification via `open_clip`
- LLM narration + TTS (v0.2)
- Google MetNet integration (v0.3, requires paid API)
- Mobile PWA (v0.4)

---

## Configuration

Copy `.env.example` to `.env` and fill in the keys you have:

```bash
cp .env.example .env
```

All keys are optional. See [.env.example](.env.example) for full documentation.

---

## Privacy

skywatch is designed with privacy as a first principle:

- **No browser Geolocation API** is ever called. Location is resolved server-side from IP at city level only.
- **No IP–query pair logging**. The IP used for geolocation is discarded immediately after resolution.
- **No user tracking**, cookies, or analytics by default.
- **No persistent location storage** unless the user explicitly saves a preference.

See [docs/PRIVACY.md](docs/PRIVACY.md) for the full privacy policy draft.

---

## Legal Notice — Camera Sources

> ⚠️ **IMPORTANT**: Only legally-accessible public camera sources are used.
>
> **Permitted**: Windy Webcams API (ToS-compliant), US DOT 511 state feeds (public domain), NOAA/NWS cameras (federal public data).
>
> **Never use**: Insecam, Opentopia, or any aggregator of unsecured/default-password IP cameras. These cameras have not consented to public access and using them is illegal in many jurisdictions.

See [docs/LEGAL.md](docs/LEGAL.md) for detailed legal guidance with source citations.

---

## Contributing

1. Fork the repo and create a feature branch (`git checkout -b feat/your-feature`)
2. Run the test suite: `cd services/api && pytest`
3. Ensure Python code passes `ruff check .` and `black --check .`
4. Ensure TypeScript passes `cd apps/web && npm run lint`
5. Open a pull request with a clear description

### Priority contributions welcome

- Additional forecast providers (see `services/api/app/providers/base.py` for the interface)
- Additional camera sources (see `services/api/app/cameras/base.py` for the interface)
- Fine-tuned weather classifier training (see `services/api/app/vision/README.md`)
- Translations / i18n for the frontend

---

## Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md) for the full versioned roadmap.

| Version | Theme | ETA |
|---------|-------|-----|
| v0.1 (current) | MVP: Open-Meteo + heuristic CV | Now |
| v0.2 | LLM narration, TTS, avatar anchor | Q3 2025 |
| v0.3 | Real Earth-2 NIM inference | Q4 2025 |
| v0.4 | Mobile PWA, offline support | Q1 2026 |

---

## License

MIT — see [LICENSE](LICENSE).

---

*skywatch is an independent open-source project and is not affiliated with NVIDIA, ECMWF, Google, or any commercial weather provider.*
