# skywatch Roadmap

---

## v0.1 — MVP (Current)

**Theme**: Runnable proof of concept. Real weather, no fluff.

### ✅ Completed
- Open-Meteo provider (ECMWF IFS) — fully working, no key required
- Weighted ensemble layer with confidence intervals
- IP-based city geolocation (ephemeral, privacy-safe)
- Manual cascading location picker (country → region → city)
- Next.js 15 frontend with Tailwind CSS
- 7-day forecast chart (Recharts)
- Webcam grid with heuristic CV classifier (HSV + Sobel)
- Windy Webcams API stub (key required)
- US DOT 511 camera example (UDOT)
- Docker Compose for single-command startup
- Full legal and privacy documentation

### 🔲 Known Gaps / TODOs
- EfficientNet-B0 fine-tuning pipeline (scripts/train_classifier.py exists, model not trained)
- NVIDIA Earth-2 NIM (stub only — returns mock data)
- OpenWeatherMap (works if key provided, not stubbed with real fallback data)
- Global camera discovery beyond Windy + UDOT

---

## v0.2 — AI Narration

**Theme**: Add a voice and personality to weather data.

**Target**: Q3 2025

### Planned Features

#### LLM Narration
- Integrate an LLM (e.g., GPT-4o, Claude Haiku, Llama 3) to generate natural-language weather summaries
- Example output: *"Dhaka is looking at a humid 32°C afternoon with a 60% chance of the monsoon arriving by evening. Three nearby cameras confirm overcast skies."*
- Configurable tone: formal, casual, broadcast-style
- Multi-language support via LLM instruction
- Cost cap: configurable token budget per request

#### Text-to-Speech (TTS)
- OpenAI TTS or ElevenLabs for high-quality narration audio
- Caching: audio cached per forecast fingerprint (hash of conditions + location + date)
- Streaming: streamed to browser for fast time-to-first-audio

#### Avatar / Visual Anchor
- Animated SVG or Lottie avatar that reacts to weather conditions
- Clear → sunny animation; Rain → rain drops; Snow → snowflake drift
- No uncanny-valley rendered faces — geometric/abstract style

#### Privacy
- LLM requests contain only weather data (temperature, conditions, location name) — **no user identifiers**
- TTS audio cached on server, keyed by forecast hash only

---

## v0.3 — Real Earth-2 NIM Inference

**Theme**: Upgrade the ensemble with a true AI weather model.

**Target**: Q4 2025

### Planned Features

#### NVIDIA Earth-2 NIM Integration
- Complete the `nvidia_earth2.py` provider stub
- Source initial atmospheric conditions from:
  - ERA5 reanalysis (via CDS API or Copernicus) for hindcasts
  - GFS analysis (NOAA NOMADS, free) for real-time
- Parse FourCastNet's 73-variable output (temperature, wind, geopotential, humidity)
- Map to `ForecastResult` schema
- Visualise ensemble spread between FourCastNet and ECMWF IFS

#### EfficientNet-B0 Classifier
- Fine-tune on FWID + Kaggle Weather Recognition datasets
- Publish model weights under CC BY 4.0
- CLIP zero-shot fallback using `open_clip`
- Accuracy target: ≥85% on held-out test set

#### MaxMind GeoLite2 (Self-hosted Geolocation)
- Replace ipapi.co with a local MaxMind GeoLite2 MMDB file
- Monthly auto-update script
- Zero outbound IP lookup — full privacy

#### Additional Camera Sources
- Norway traffic cameras (NPRA)
- Transport for NSW (TfL-style open data)
- NOAA buoy cameras

---

## v0.4 — Mobile PWA

**Theme**: Works everywhere, even offline.

**Target**: Q1 2026

### Planned Features

#### Progressive Web App
- `next-pwa` with Workbox service worker
- Offline forecast cache (last successful response)
- Install prompt for iOS Safari + Android Chrome
- Push notifications for severe weather alerts (opt-in only)

#### Mobile UX
- Bottom sheet navigation (mobile-native pattern)
- Swipe gestures for forecast days
- Haptic feedback on condition changes
- Dark mode system-preference detection

#### Alerts & Notifications
- NWS CAP feed integration (US)
- Meteoalarm (Europe)
- Push notification for: severe thunderstorm, tornado, flash flood, blizzard
- All alert delivery is local-first — no server-side user registry

---

## v0.5 — Community & Observational Data

**Theme**: Crowdsourced weather reports, METAR integration, amateur weather stations.

**Target**: Q2 2026

### Planned Features

- METAR/ASOS integration for airport weather observations
- Personal weather station aggregation (Weather Underground API or direct MQTT)
- Community reports: anonymous condition reports from app users
- Peer-to-peer report sync (WebRTC mesh for regional consensus)

---

## Long-term Vision

- Federated skywatch instances: organisations can run private instances that share anonymised condition reports
- Open training data pipeline: CVconditions observed by the app contribute to a public training dataset (opt-in, anonymised)
- Hardware integration: Raspberry Pi + camera as a skywatch node — plug in and join the network
