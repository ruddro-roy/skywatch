# skywatch Roadmap

---

## v0.1 — MVP (Current)

###  Completed
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

###  Known Gaps
- EfficientNet-B0 fine-tuning pipeline (scripts/train_classifier.py exists, model not trained)
- NVIDIA Earth-2 NIM (stub only,  returns mock data)
- OpenWeatherMap (works if key provided, not stubbed with real fallback data)
- Global camera discovery beyond Windy + UDOT

---

#### Text-to-Speech (TTS)
- OpenAI TTS or ElevenLabs for high-quality narration audio
- Caching: audio cached per forecast fingerprint (hash of conditions + location + date)
- Streaming: streamed to browser for fast time-to-first-audio

#### Avatar / Visual Anchor
- Avatar that reacts to weather conditions
- Clear → sunny animation; Rain → rain drops; Snow → snowflake drift
- No uncanny-valley rendered faces, geometric/abstract style


## Long-term Vision

- Federated skywatch instances: organisations can run private instances that share anonymised condition reports
- Open training data pipeline: CVconditions observed by the app contribute to a public training dataset (opt-in, anonymised)
- Hardware integration: Raspberry Pi + camera as a skywatch node,  plug in and join the network
