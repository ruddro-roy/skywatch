# Camera proof

One of the ideas in skywatch is to cross-check a forecast against a real public camera. Below are three independent checks, each captured on April 17, 2026. All three use public, legally accessible sources. No scraping of unsecured cameras.

## 1. E6 Alsgård, Nordland, Norway

Source: [Statens vegvesen](https://kamera.atlas.vegvesen.no/api/images/3000946_1), Norwegian Licence for Open Government Data.

![E6 Alsgård](docs/cameras/norway-alsgard-e6.jpg)

- Frame timestamp (in image): `2026-04-17 08:17:02`
- Coordinates: 65.83 N, 13.31 E, 49 m elevation
- Visual: daylight, dry road, thin high cloud, coniferous forest, no precipitation
- Open-Meteo at capture minute: `3.6°C`, feels like `1.1°C`, `29%` cloud cover, `70%` humidity, `1.4 km/h` wind, WMO code `1` (mainly clear)
- Match: forecast and camera agree

## 2. E6 Aisaroaivi, Finnmark, Norway

Source: [Statens vegvesen](https://kamera.atlas.vegvesen.no/api/images/2000065_2), NLOD.

![E6 Aisaroaivi](docs/cameras/norway-aisaroaivi-skaidi.jpg)

- Frame timestamp: `2026-04-17 08:16:16`
- Coordinates: 70.28 N, 24.59 E, 238 m elevation, near 70° N
- Visual: arctic tundra, heavy snow on ground, cleared road, mixed sun and high cloud
- Open-Meteo at capture minute: `2.1°C`, feels like `-0.5°C`, `80%` cloud cover, `96%` humidity, `5.4 km/h` wind, WMO code `3` (overcast)
- Match: consistent. The near-freezing temperature explains the lingering snow; the overcast reading matches the hazy look of the frame.

## 3. NOAA GLERL, Chicago, USA

Source: [NOAA Great Lakes Environmental Research Laboratory](https://www.glerl.noaa.gov/metdata/chi/chi01.jpg), public domain.

![NOAA GLERL Chicago](docs/cameras/chicago-glerl-chi01.jpg)

- Frame timestamp: `2026-04-17 01:00 CDT`
- Station: Harrison-Dever Crib, Lake Michigan, ~2.75 miles offshore Chicago
- Visual: night, near-black, no visible skyline, one distant light
- Station's own readings at the same moment: `6.7°C` air, `6.8°C` dew point, `100%` relative humidity, `0.0 kts` wind from the east
- Match: dew point equal to air temperature at 100% humidity is the textbook fog signature. A near-black, featureless frame at night is what you would expect if the camera is sitting inside fog.

## Capture metadata

Full capture metadata, including raw Open-Meteo JSON responses, is in [docs/cameras/readings.json](docs/cameras/readings.json).

## Why these sources

- **Statens vegvesen (Norway)**: Open government data, NLOD license allows redistribution with attribution. Road cameras are operated for public travel information.
- **NOAA GLERL (USA)**: Federal government data in the public domain.

Deliberately not used: Insecam, Opentopia, or any aggregator of unsecured or default-password IP cameras. These cameras have not consented to public access and using them is illegal in many jurisdictions. See [docs/LEGAL.md](docs/LEGAL.md).
