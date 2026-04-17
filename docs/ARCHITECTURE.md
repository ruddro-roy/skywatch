# skywatch, Architecture & System Design

## Overview

skywatch is a hybrid weather intelligence system built around three core pillars:

1. **Forecast Fusion**, Weighted ensemble of multiple AI weather model providers
2. **Computer-Vision Ground Truth**, Frame-level condition classification from public webcams
3. **Privacy-by-Design**, No Geolocation API, ephemeral IP resolution, zero logging of identifiable data

---

## Component Diagram

```
┌─────────────────────────────── BROWSER ──────────────────────────────────┐
│ │
│ ┌────────────────────────────────────────────────────────────────────┐ │
│ │ Next.js 15 App Router │ │
│ │ │ │
│ │ page.tsx │ │
│ │ ├─ LocationPicker (country → admin1 → city cascading) │ │
│ │ ├─ CurrentConditions (live conditions + CV-verified label) │ │
│ │ ├─ ForecastPanel (7-day chart + per-provider breakdown) │ │
│ │ ├─ CameraGrid (webcam thumbs + detected condition badge) │ │
│ │ └─ EnsembleConfidence (provider weights + uncertainty bar) │ │
│ │ │ │
│ │ app/api/geoip/route.ts (Edge route: IP → city, ephemeral) │ │
│ └───────────────────────────────┬─────────────────────────────────────┘ │
│ │ HTTP/JSON │
└──────────────────────────────────│──────────────────────────────────────┘
 │
 ┌─────────▼──────────┐
 │ FastAPI (Python) │
 │ │
 │ /api/geoip │◄── IP from X-Forwarded-For
 │ /api/weather │◄── lat, lon params
 │ /api/cameras │◄── lat, lon, radius params
 │ /health │
 └─────────┬──────────┘
 │
 ┌────────────────────┼─────────────────────┐
 │ │ │
 ┌──────────▼──────┐ ┌─────────▼──────────┐ ┌──────▼────────────┐
 │ geolocation.py │ │ ensemble.py │ │ cameras/ │
 │ │ │ │ │ discovery.py │
 │ ipapi.co API │ │ WeightedEnsemble │ │ │
 │ (city-level) │ │ ───────────────── │ │ ┌─────────────┐ │
 │ IP discarded │ │ normalize() │ │ │ windy.py │ │
 │ after use │ │ fuse() │ │ │ dot_us.py │ │
 └─────────────────┘ │ confidence() │ │ └──────┬──────┘ │
 └─────────┬──────────┘ │ │ │
 │ │ ┌──────▼──────┐ │
 ┌────────────────────┤ │ │ vision/ │ │
 │ │ │ │ classifier │ │
 ┌──────────▼──────┐ ┌──────────▼─────────┐ │ └─────────────┘ │
 │ open_meteo.py │ │ openweathermap.py │ └───────────────────┘
 │ WORKING │ │ needs key │
 │ ECMWF IFS │ │ OWM current+fcst │
 └─────────────────┘ └────────────────────┘
 ┌─────────────────────────────────────────┐
 │ nvidia_earth2.py │ metnet_stub.py │
 │ TODO (NIM) │ TODO (paid) │
 └─────────────────────────────────────────┘
```

---

## Data Flow: Weather Request

```
1. Browser loads page.tsx
2. page.tsx calls /api/geoip (Edge route) → returns {city, country, lat, lon}
 - IP extracted from X-Forwarded-For / CF-Connecting-IP headers
 - Forwarded to FastAPI /api/geoip
 - ipapi.co resolves to city level
 - IP discarded immediately, only city metadata returned
 - If geolocation fails, frontend falls back to manual location picker

3. page.tsx calls FastAPI GET /api/weather?lat=&lon=
 - ensemble.py queries all configured providers in parallel (asyncio.gather)
 - Each provider returns a normalised ForecastResult
 - WeightedEnsemble.fuse() computes:
 weighted_mean = Σ(weight_i × value_i) / Σ(weight_i)
 stddev = sqrt(Σ(weight_i × (value_i − mean)²) / Σ(weight_i))
 confidence = 1 − (stddev / range) (normalised 0–1)
 - Response includes per-provider breakdown + ensemble result

4. page.tsx calls FastAPI GET /api/cameras?lat=&lon=&radius=50
 - discovery.py queries all enabled camera sources in parallel
 - Returns list of CameraResult objects with thumbnail URLs
 - For each camera, vision/classifier.py classifies the latest frame:
 HSV heuristic: saturation → rain/fog, value → day/night
 Edge density (Sobel): high → rain/snow, low → fog
 - Returns condition label + confidence per camera

5. Frontend renders dashboard:
 - CurrentConditions: ensemble temperature + CV-verified condition
 - ForecastPanel: Recharts line chart, per-provider toggle
 - CameraGrid: thumbnails + condition badge overlay
 - EnsembleConfidence: horizontal bar of provider weights
```

---

## Forecast Fusion Logic

### Provider Weights

Weights are assigned based on:

| Factor | Description |
|--------|-------------|
| `lead_time_skill` | Provider's documented RMSE at forecast horizon |
| `regional_reliability` | Known accuracy in tropical / polar / arid zones |
| `recency` | How recently the model was run (ECMWF runs 4×/day) |
| `availability` | Weight reduced to 0 if provider returns an error |

Default weights (adjustable in `config.py`):

```python
DEFAULT_WEIGHTS = {
 "open_meteo": 1.0, # ECMWF IFS, reliable global baseline
 "openweathermap": 0.7, # GFS-based, good for short range
 "nvidia_earth2": 1.2, # FourCastNet, higher weight when active (v0.3)
 "metnet": 0.9, # Google MetNet (v0.3)
}
```

### Normalisation

All providers map their outputs to a common schema (`ForecastResult`) defined in `schemas.py`:

- Temperature in Celsius
- Precipitation probability 0–1
- Wind speed in m/s
- WMO weather code
- Hourly + daily granularity

---

## Computer-Vision Pipeline

### MVP: Heuristic Classifier (no model download)

```
frame (JPEG) → PIL Image → HSV array
 │
 ┌─────────────────────┼─────────────────────┐
 │ │ │
 mean_saturation mean_value (V) edge_density
 (chroma richness) (brightness) (Sobel gradient)
 │ │ │
 high S → rain/wet low V → night/fog high E → precip
 low S → fog/snow high V → day low E → fog/clear
 │ │ │
 └─────────────────────▼─────────────────────┘
 rule-based fusion
 │
 condition label
 {clear, cloudy, fog, rain, snow}
```

### v0.2: EfficientNet-B0 Fine-tuned

- Base model: `torchvision.models.efficientnet_b0(pretrained=True)`
- Head: 1280 → 256 → 5 classes
- Training data: FWID (Flickr Weather Image Dataset), RFS dataset, Kaggle Weather Recognition
- Expected accuracy: ~87% on held-out test set
- See `services/api/app/vision/README.md` for training plan

### v0.2: CLIP Zero-Shot

- Model: `open_clip` with `ViT-B/32` weights
- Prompts: `"a photo taken in clear weather"`, `"rain falling in the image"`, etc.
- No fine-tuning required, works out of the box if `open_clip` is installed

---

## Privacy Architecture

```
REQUEST PROCESSING RESPONSE
───────── ────────── ────────
Client IP ──────────────► ipapi.co lookup ──────────── ► {city, lat, lon}
 (never logged) (IP discarded)
 ▼
 stored only in
 React state (memory)
 cleared on page unload
```

Key decisions:
- `X-Forwarded-For` header is read once, passed to ipapi.co, then discarded
- No IP is written to any log file, database, or analytics system
- Users can override with manual location picker, IP never used
- No cookies, no localStorage for location data
- No third-party analytics scripts

---

## Directory Structure

```
skywatch/
├── apps/web/ Next.js 15 frontend
│ ├── app/ App Router pages
│ ├── components/ React components
│ └── lib/ API client
├── services/api/ FastAPI backend
│ ├── app/
│ │ ├── providers/ Forecast model integrations
│ │ ├── cameras/ Webcam source integrations
│ │ ├── vision/ CV classifier
│ │ └── routes/ HTTP route handlers
│ └── tests/
├── docs/ Architecture, legal, privacy docs
└── scripts/ Dev tooling, training scripts
```

---

## Scalability Notes

- All HTTP calls use `httpx.AsyncClient`, providers are queried in parallel
- Provider timeouts are configurable (default 10s), slow providers are skipped gracefully
- The ensemble works with any subset of providers ≥ 1
- Camera discovery is paginated and radius-limited to prevent abuse
- Rate limiting headers from upstream APIs are respected and surfaced in logs

---

## Future: Earth-2 NIM Integration (v0.3)

NVIDIA's Earth-2 NIM exposes FourCastNet and CorrDiff via a REST API at `integrate.api.nvidia.com`. The stub in `nvidia_earth2.py` documents the expected request/response schema. Full integration requires:

1. An NGC API key with Earth-2 NIM access
2. Providing initial conditions as NetCDF or JSON (sourced from ERA5 or GFS analysis)
3. Parsing the 73-variable output and mapping to `ForecastResult`

Reference: https://docs.api.nvidia.com/nim/reference/nvidia-fourcastnet
