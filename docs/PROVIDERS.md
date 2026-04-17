# skywatch — Provider Reference

All forecast and camera providers, with license, free-tier limits, and integration status.

---

## Forecast Providers

| Provider | Model | License | Free Tier | Key Required | Status | Notes |
|----------|-------|---------|-----------|--------------|--------|-------|
| [Open-Meteo](https://open-meteo.com) | ECMWF IFS, GFS, ICON | CC BY 4.0 | Unlimited (non-commercial) | No | ✅ Working | Best free option; 7-day global; 1-hour resolution |
| [OpenWeatherMap](https://openweathermap.org/api) | GFS-based | Proprietary | 1,000 calls/day | Yes | ⚠️ Key needed | Free tier: current + 5-day 3-hour forecast |
| [NVIDIA Earth-2 NIM](https://docs.api.nvidia.com/nim/reference/nvidia-fourcastnet) | FourCastNet / CorrDiff | Proprietary | Credit-based (~$0.018/call) | Yes | 🔲 Stub | AI-native; requires initial conditions input |
| [Google MetNet-3](https://cloud.google.com/blog/topics/developers-practitioners/metnet-3-google-deepminds-weather-model) | MetNet-3 | Proprietary | No public API | Enterprise | 🔲 Stub | Contact Google for access |
| [ECMWF Open Data](https://www.ecmwf.int/en/forecasts/datasets/open-data) | ECMWF AIFS | CC BY 4.0 | Free (direct GRIB download) | No | 🔲 TODO | Requires GRIB parsing (cfgrib) |
| [Norwegian Meteorological Institute](https://api.met.no) | HARMONIE-AROME | NLOD / CC BY 4.0 | Free | No | 🔲 TODO | Excellent for northern Europe and Arctic |
| [Meteomatics](https://www.meteomatics.com/en/weather-api) | Ensemble blend | Proprietary | 500 calls/day (dev) | Yes | 🔲 Future | High-resolution point forecasts |

### Open-Meteo Details

| Field | Value |
|-------|-------|
| URL | https://api.open-meteo.com/v1/forecast |
| Auth | None |
| Models | ECMWF IFS, GFS, ICON, Gem, ARPEGE |
| Resolution | 0.1°–0.25° global |
| Horizon | Up to 16 days |
| Update frequency | 4× per day |
| Variables | Temperature, precipitation, wind, humidity, pressure, UV index, WMO codes |
| Docs | https://open-meteo.com/en/docs |
| ToS | https://open-meteo.com/en/terms |

---

## Camera / Webcam Sources

| Source | Coverage | License | Free Tier | Key Required | Status | Notes |
|--------|----------|---------|-----------|--------------|--------|-------|
| [Windy Webcams API v3](https://api.windy.com/webcams) | Global (50k+ cams) | Proprietary + ToS | 500 calls/day | Yes | ⚠️ Key needed | Best global coverage; thumbnails + metadata |
| [UDOT Traffic](https://udottraffic.utah.gov/) | Utah, USA | Public domain | Unlimited | No | ⚠️ US-only example | JSON feed; real-time thumbnails |
| [511GA](https://511ga.org) | Georgia, USA | Public domain | Unlimited | No | 🔲 TODO | State DOT feed |
| [NOAA/NWS](https://www.weather.gov) | USA + global buoys | Public domain | Unlimited | No | 🔲 TODO | NOAA weather cameras |
| [Transport for NSW](https://opendata.transport.nsw.gov.au/) | New South Wales, AU | CC BY 4.0 | Unlimited | Yes (free) | 🔲 TODO | Traffic cameras |
| [TfL Unified API](https://api.tfl.gov.uk) | London, UK | OGL v3 | 500 calls/min | No | 🔲 TODO | Traffic + tunnel cameras |
| [Finland FMI](https://en.ilmatieteenlaitos.fi/open-data) | Finland | CC BY 4.0 | Unlimited | No | 🔲 TODO | Weather station cameras |

### Windy Webcams API v3 Details

| Field | Value |
|-------|-------|
| URL | https://api.windy.com/api/webcams/v3/webcams |
| Auth | `x-windy-api-key` header |
| Endpoints | `/webcams` (search), `/webcams/{id}` (detail), `/webcams/{id}/images` (thumbnails) |
| Parameters | `lat`, `lon`, `radius` (km), `limit`, `offset` |
| Rate limit | 500/day (free), 5,000/day (pro) |
| ToS | https://api.windy.com/webcams/docs#terms |
| Attribution | Must display "Windy.com" and link to camera page |

---

## Geolocation Providers

| Provider | Method | License | Free Tier | Key Required | Status |
|----------|--------|---------|-----------|--------------|--------|
| [ipapi.co](https://ipapi.co) | IP → city | Proprietary | 1,000 req/day (no key) / 30,000/month (free key) | No (optional) | ✅ Working |
| [ip-api.com](https://ip-api.com) | IP → city | Proprietary | 45 req/min (no HTTPS) | No | 🔲 Fallback option |
| [ipinfo.io](https://ipinfo.io) | IP → city | Proprietary | 50,000 req/month | Yes | 🔲 Fallback option |
| [MaxMind GeoLite2](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data) | IP → city (local DB) | CC BY-SA 4.0 | Free (self-hosted) | Reg. required | 🔲 TODO (v0.3 for self-hosting) |

### Privacy Comparison

| Provider | Logs IP? | GDPR DPA | Self-host option |
|----------|----------|----------|------------------|
| ipapi.co (apilayer) | Unknown — use ephemerally | Check https://apilayer.com/privacy | No |
| ip-api.com | Unknown | No public DPA | No |
| MaxMind GeoLite2 | No (local DB) | N/A (local) | Yes (download MMDB) |

> **Recommendation for production v0.3**: Switch to MaxMind GeoLite2 with a local MMDB file. No outbound IP lookup; full control. Requires monthly DB update script.

---

## AI / ML Models (Vision)

| Model | Task | License | Source | Status |
|-------|------|---------|--------|--------|
| Heuristic (HSV + Sobel) | Weather classification | N/A | Custom | ✅ Working (MVP) |
| EfficientNet-B0 | Weather classification | Apache 2.0 | torchvision pretrained | 🔲 TODO |
| MobileNetV3-Small | Weather classification | Apache 2.0 | torchvision pretrained | 🔲 TODO |
| CLIP ViT-B/32 | Zero-shot classification | MIT | open_clip | 🔲 TODO |

### Training Datasets

| Dataset | Images | Classes | License | URL |
|---------|--------|---------|---------|-----|
| FWID (Flickr Weather Image Dataset) | 69,079 | 10 | CC BY-NC 4.0 | https://github.com/wzgwzg/FWID |
| RFS (Rain/Fog/Sunshine) | ~2,000 | 3 | Custom | Various |
| Kaggle Weather Recognition | 6,862 | 11 | CC0 | https://www.kaggle.com/datasets/jehanbhathena/weather-dataset |
| MWD (Multi-class Weather Dataset) | 2,041 | 4 | CC BY 4.0 | https://www.kaggle.com/datasets/pratik2901/multiclass-weather-dataset |
