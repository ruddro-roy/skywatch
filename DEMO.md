# 📸 skywatch — First Demo (v0.1)

> **This is the first working demo of skywatch**, captured on **April 17, 2026** from the actual running application.
>
> All screenshots below show **real live data** from the Open-Meteo / ECMWF IFS forecast provider — nothing is mocked, stubbed, or photoshopped.

---

## 🌍 What you're looking at

skywatch is a privacy-first, hybrid AI weather prototype that:

- **Fuses multiple forecast models** into a single ensemble prediction (Open-Meteo active; NVIDIA Earth-2, OpenWeatherMap, Google MetNet-3 wired up as stubs ready for API keys)
- **Never uses the browser Geolocation API** — location is resolved from the server IP at city level and discarded immediately
- **Verifies conditions with computer vision** on legally-accessible public webcams (Windy API, US DOT 511, NOAA)
- **Works anywhere on Earth** with no regional bias

Live at commit `main` · [github.com/ruddro-roy/skywatch](https://github.com/ruddro-roy/skywatch)

---

## 1. Hero view — Dhaka, Bangladesh

IP-resolved city, real-time ensemble forecast, all four provider slots visible (only Open-Meteo active in v0.1):

![Hero view – Dhaka](docs/screenshots/02-hero-dhaka.png)

**What the screenshot proves:**
- ✅ Live temperature `31°C, feels like 39°C` — fetched from Open-Meteo's ECMWF IFS endpoint at capture time
- ✅ Ensemble confidence bar rendering correctly (100% agreement because only one provider is active)
- ✅ All four provider rows visible with proper inactive/active labels
- ✅ "IP-resolved, not stored" microcopy — privacy-first messaging
- ✅ Clean dark theme, `v0.1` badge, no placeholder boxes

---

## 2. Full dashboard — Dhaka

Scrolled view showing the 7-day forecast chart (Recharts), day-by-day cards, and the camera discovery section:

![Full dashboard – Dhaka](docs/screenshots/01-dashboard-dhaka.png)

---

## 3. Location switching — Tokyo, Japan

Same session, switched to Tokyo via the cascading search picker — proves the app works globally without regional bias:

![Full dashboard – Tokyo](docs/screenshots/03-dashboard-tokyo.png)

Tokyo pulled a different forecast (`19°C, feels like 18°C, 41% humidity`) and showed rain arriving Thursday with 69% precipitation probability — real ECMWF IFS output for Tokyo at capture time.

---

## 4. Ensemble + forecast detail

The ensemble confidence panel and 7-day chart close-up, showing per-provider weights and the fused output temperature:

![Ensemble and forecast](docs/screenshots/05-ensemble-forecast.png)

**Key elements:**
- Per-provider weight display (Open-Meteo `100% weight`, others `inactive · 0% weight`)
- Fused temperature readout (`19°C`)
- Daily cards with max/min/precipitation probability
- `ToS-compliant sources only` badge on the cameras section

---

## 5. Nearby cameras section

The camera grid area — shows the CV pipeline is hooked up and waiting for a Windy API key to populate with real camera thumbnails:

![Cameras section](docs/screenshots/04-cameras-section.png)

In v0.1, this panel gracefully handles the "no Windy key configured" state. Drop a `WINDY_API_KEY` into `.env` and it immediately lights up with real webcam thumbnails labeled by the heuristic CV classifier (HSV + Sobel edge analysis) — or by EfficientNet-B0 once you run `scripts/train_classifier.py` on the FWID dataset.

---

## 🔧 Reproducing this demo locally

All screenshots above were captured with the exact commands below on a fresh clone, **with zero API keys configured**:

```bash
git clone https://github.com/ruddro-roy/skywatch
cd skywatch

# Terminal 1 — API
cd services/api
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# Terminal 2 — Web
cd apps/web
npm install
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000 npm run dev
```

Then open `http://localhost:3000` — you'll see the same dashboard with live data for your city (or Dhaka as fallback).

---

## 📊 What's live vs. what's stubbed (honest status)

| Feature | v0.1 status |
|---|---|
| Open-Meteo / ECMWF IFS forecast | ✅ Fully live, no API key needed |
| Privacy-first IP geolocation (ipapi.co) | ✅ Fully live |
| Cascading city search picker | ✅ Fully live (Open-Meteo Geocoding) |
| Ensemble fusion engine | ✅ Fully live (33 passing tests) |
| 7-day Recharts forecast chart | ✅ Fully live |
| CV heuristic classifier (HSV + Sobel) | ✅ Fully live |
| OpenWeatherMap provider | 🔑 Works when `OPENWEATHERMAP_API_KEY` is set |
| Windy Webcams integration | 🔑 Works when `WINDY_API_KEY` is set |
| US DOT 511 camera integration | ✅ Enabled by default (public data) |
| NVIDIA Earth-2 / FourCastNet NIM | 🏗️ Documented stub — v0.3 target |
| EfficientNet-B0 / CLIP zero-shot | 🏗️ Training pipeline ready in `scripts/train_classifier.py` — v0.2 target |
| Google MetNet-3 | 🏗️ No public API exists yet — placeholder |
| LLM narration / AI anchor | 🏗️ v0.2 roadmap |

---

## 🙏 Credits

- **Forecast data:** [Open-Meteo](https://open-meteo.com) (ECMWF IFS)
- **Geolocation:** [ipapi.co](https://ipapi.co) free tier
- **Architecture reference:** [NVIDIA Earth-2 family](https://docs.nvidia.com/nim/earth-2/) (open-sourced Jan 2026)
- **Frameworks:** [Next.js 15](https://nextjs.org), [FastAPI](https://fastapi.tiangolo.com), [Tailwind CSS](https://tailwindcss.com), [Recharts](https://recharts.org)

---

**📅 Captured:** April 17, 2026
**🏷️ Version:** v0.1 (first demo)
**📄 License:** [MIT](LICENSE)
