# skywatch — Legal Guidance: Camera Sources

> This document provides guidance on the legal and ethical use of public webcam data in skywatch. It is not legal advice. Consult a qualified attorney for jurisdiction-specific questions.

---

## Summary

| Source | Legal Status | Usage in skywatch |
|--------|-------------|-------------------|
| Windy Webcams API |  Permitted (ToS-compliant) | Full integration |
| US DOT 511 feeds |  Permitted (public domain) | Example integration |
| NOAA/NWS cameras |  Permitted (federal public data) | TODO stub |
| Transport for NSW, TfL (UK) |  Permitted (open data licenses) | TODO stub |
| Insecam |  **NEVER USE** | Explicitly excluded |
| Opentopia |  **NEVER USE** | Explicitly excluded |
| Any default-password IP cams |  **NEVER USE** | Explicitly excluded |

---

## Permitted Sources

### 1. Windy Webcams API

**URL**: https://api.windy.com/webcams  
**ToS**: https://api.windy.com/webcams/docs#terms  
**License**: Commercial use requires paid plan; weather apps qualify for API access  
**What's permitted**: Fetching thumbnail images, camera metadata (name, lat/lon, category), and weather condition tags via the official API.  
**What's NOT permitted**: Storing images beyond the session, re-hosting thumbnails, scraping the Windy.com website directly.

Key ToS provisions:
- Must display attribution: "Weather camera provided by Windy.com"
- Must link back to the camera's Windy.com page when displaying thumbnails
- Rate limits must be respected (varies by plan)

### 2. US Department of Transportation 511 Traffic Cameras

**Reference**: https://www.transportation.gov/accessibility/511  
**Legal basis**: 23 U.S.C. § 154 — federal highway data is public domain  
**State examples**:
- Utah DOT (UDOT): https://udottraffic.utah.gov/ — JSON feed at `api.udottraffic.utah.gov`
- Georgia 511: https://511ga.org — public camera feed (see `cameras/dot_us.py`)
- California: https://cwwp2.dot.ca.gov/documentation/cctv/cctv.htm

**What's permitted**: Real-time fetching of camera images and metadata from official state DOT APIs for weather/safety informational purposes.  
**Limitations**: Some state DOTs require a data sharing agreement for commercial use. skywatch's open-source, non-commercial use is generally covered.

### 3. NOAA / National Weather Service Cameras

**Reference**: https://www.noaa.gov/information-technology/open-data-dissemination  
**Legal basis**: U.S. federal government works are in the public domain (17 U.S.C. § 105)  
**What's permitted**: All NOAA and NWS camera imagery and data is public domain.

### 4. Other Public-Sector / Open-Data Cameras

The following require per-jurisdiction verification but are generally permissible:
- **Transport for NSW (Australia)**: Creative Commons license — https://opendata.transport.nsw.gov.au/
- **Transport for London (TfL)**: Open Government License — https://tfl.gov.uk/info-for/open-data-users/
- **Finnish Meteorological Institute**: CC BY 4.0 — https://en.ilmatieteenlaitos.fi/open-data

---

## Prohibited Sources

### 1. Insecam (insecam.org)

**Why it's prohibited**: Insecam aggregates unsecured IP cameras that were never intended for public access. These cameras use default manufacturer passwords (e.g., "admin"/"admin"). Accessing them:
- Constitutes unauthorized access under the U.S. Computer Fraud and Abuse Act (18 U.S.C. § 1030)
- Violates the UK Computer Misuse Act 1990
- Violates GDPR Article 6 (lawful basis) in the EU — these cameras have not consented to public streaming
- May constitute wiretapping under various state laws

**References**:
- FTC guidance on IoT security and unauthorized access: https://www.ftc.gov/tips-advice/business-center/guidance/internet-things-businesses
- UK ICO on CCTV and data protection: https://ico.org.uk/for-organisations/guide-to-data-protection/key-dp-themes/surveillance/

### 2. Opentopia (opentopia.com)

**Why it's prohibited**: Same category as Insecam — aggregates cameras with default credentials. Using this service:
- Violates the same laws cited above
- Exposes contributors and users to criminal and civil liability

### 3. Any Aggregator of Default-Credential Cameras

**Rule**: Never use any website or service that obtains cameras by exploiting default manufacturer passwords or misconfiguration. The ethical test: "Did the camera owner intend for this to be publicly accessible?"

---

## The AccuWeather / Reveal Mobile Precedent (Anti-Pattern)

In 2017, AccuWeather was found to be sending user location data (including Wi-Fi network names) to Reveal Mobile, a third-party monetization company, even when users had disabled location sharing. This case illustrates the reputational and legal risk of:

1. Collecting more location data than disclosed in privacy policies
2. Sharing location data with third parties without informed consent
3. Using indirect identifiers (Wi-Fi SSIDs) as proxies for location

**References**:
- BuzzFeed investigation (2017): https://www.buzzfeednews.com/article/nicolenguyen/accuweather-ios-app-sending-location-data-even-if-you-say-no
- AccuWeather statement and patch: https://www.accuweather.com/en/press/accuweather-statement-on-sdk-partner-data-collection/70033

**skywatch's approach**: We never use browser geolocation, never log IP-location pairs, and never share location data with third parties. The IP used for initial city detection is discarded immediately and never stored.

---

## GDPR / CCPA Considerations

### GDPR (EU/EEA users)

- IP address is personal data under GDPR Article 4(1)
- skywatch processes IP addresses lawfully under Article 6(1)(f) (legitimate interests — providing a weather service) but only ephemerally
- No IP is retained beyond the single request that triggered geolocation
- Users in the EU have the right to use the manual location picker to avoid IP processing entirely
- No data is transferred to third countries beyond the ephemeral ipapi.co lookup (ipapi.co is operated by apilayer — verify their DPA at https://apilayer.com/privacy)

### CCPA (California users)

- skywatch does not "sell" personal information as defined by California Civil Code § 1798.140
- No personal information is retained, making most CCPA rights (deletion, access) moot
- The privacy policy draft in `PRIVACY.md` reflects these commitments

### Recommendation

For a production deployment, add a privacy banner for EU users explaining the ephemeral IP lookup and providing a "Use manual location" opt-out button.

---

## Contributor Guidelines

When adding a new camera source to skywatch:

1. **Verify legal basis**: Must be a public API with explicit ToS permitting weather/informational use
2. **Document in PROVIDERS.md**: Add the source with license, ToS URL, and free-tier limits
3. **No credentials in code**: Use environment variables only
4. **Rate limit compliance**: Implement backoff and respect rate limit headers
5. **Attribution**: Display required attribution in the CameraGrid component
6. **Pull request checklist**: Include a "Legal basis" section in the PR description
