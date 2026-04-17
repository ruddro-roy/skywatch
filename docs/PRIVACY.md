# skywatch — Privacy Policy (Draft)

* This is a draft policy for the open-source skywatch project. Operators who deploy skywatch must review and adapt this policy for their specific deployment, jurisdiction, and any additional data processing they perform.*

---

## Summary

| Question | Answer |
|----------|--------|
| Do you collect my location? | Only at city level, only when you load the page, only to show weather for your city. |
| Do you store my IP address? | No. Your IP is used once to guess your city, then immediately discarded. |
| Do you use browser Geolocation? | **Never.** skywatch deliberately does not use the browser Geolocation API. |
| Do you use cookies? | No tracking cookies. No analytics cookies. No cross-site cookies. |
| Do you sell my data? | No. |
| Do you share my data? | Only with ipapi.co (ephemeral IP lookup). No data is retained by us. |
| Who can I contact? | Open a GitHub issue at https://github.com/your-org/skywatch |

---

## 1. Who We Are

skywatch is an open-source weather prototype. This privacy policy applies to the reference deployment at [your deployment URL]. Operators who run their own skywatch instances are responsible for their own data practices.

---

## 2. What Data We Collect

### 2.1 IP Address (Ephemeral Geolocation Only)

When you load the skywatch application, your IP address is transmitted (as is normal for any web request) and passed to [ipapi.co](https://ipapi.co) to determine your approximate city-level location. This lookup:

- Returns: country, region, city, approximate latitude/longitude
- The IP address is **not stored**, **not logged**, **not associated with your request**, and **not used for any other purpose**
- The resolved city-level location is returned to your browser and held only in browser memory for the duration of your session
- No record is retained server-side

**Legal basis (GDPR)**: Article 6(1)(f) — Legitimate interest in providing a weather service without requiring manual location input. Users may exercise their right to object by using the manual location picker instead.

### 2.2 Manual Location (Optional, User-Initiated)

If you use the location picker (country → region → city dropdown), your selected location is:
- Held in browser memory only
- Never transmitted to our servers beyond the weather query parameters (lat/lon)
- Cleared when you close or reload the page
- Optionally saved to `localStorage` only if you explicitly click "Remember my location" (feature planned for v0.2)

### 2.3 Weather Queries

When you request weather data, we transmit your latitude/longitude to:
- [Open-Meteo API](https://open-meteo.com/en/terms): Free, non-commercial use. Open-Meteo's own privacy policy applies to this transmission.
- [OpenWeatherMap](https://openweathermap.org/privacy-policy) (if configured): Their privacy policy applies.
- Windy Webcams API (if configured): [Windy.com privacy policy](https://www.windy.com/privacy) applies.

We do **not** link your lat/lon query to your IP address in any log or database.

### 2.4 What We Do NOT Collect

- We do not collect browser Geolocation (GPS/WiFi-based precise location)
- We do not use advertising trackers or analytics
- We do not set persistent tracking cookies
- We do not create user profiles or device fingerprints
- We do not collect names, email addresses, or any account information
- We do not collect usage metrics beyond standard HTTP server logs (see §2.5)

### 2.5 Server Logs

Standard HTTP server logs (nginx/uvicorn access logs) record:
- Timestamp
- HTTP method and path
- Response status code
- Response size

These logs do **not** include client IP addresses in the default skywatch configuration (access logging is disabled or IP fields are anonymised). Operators deploying skywatch are responsible for their own server log configuration.

---

## 3. Cookies and Local Storage

skywatch does not set any cookies. No third-party scripts that set cookies are loaded.

`localStorage` is only used if you explicitly opt in to "Remember my location" (planned for v0.2). This data never leaves your device.

---

## 4. Third-Party Services

| Service | Data Shared | Their Privacy Policy |
|---------|------------|---------------------|
| ipapi.co (apilayer) | Your IP address (ephemeral) | https://apilayer.com/privacy |
| Open-Meteo | Lat/lon of your location | https://open-meteo.com/en/terms |
| OpenWeatherMap (if configured) | Lat/lon of your location | https://openweathermap.org/privacy-policy |
| Windy.com (if configured) | Lat/lon query for nearby cameras | https://www.windy.com/privacy |
| UDOT 511 (if configured) | Lat/lon query | https://udottraffic.utah.gov/ |

---

## 5. Your Rights

### GDPR (EU/EEA Residents)

You have the right to:
- **Access**: Request what data we hold about you. (Answer: none, beyond the current session.)
- **Erasure**: Request deletion of your data. (Answer: no data is retained to delete.)
- **Object**: Object to processing based on legitimate interests. Use the manual location picker to avoid the IP lookup entirely.
- **Lodge a complaint**: With your national data protection authority (e.g., ICO in the UK, CNIL in France, BfDI in Germany).

### CCPA (California Residents)

skywatch does not sell personal information. No personal information is retained beyond the current request. Most CCPA rights (access, deletion, opt-out of sale) are moot because no data is retained.

---

## 6. Data Retention

| Data Type | Retention Period |
|-----------|-----------------|
| IP address | 0 seconds — discarded immediately after geolocation lookup |
| City-level location | Browser memory only — session duration |
| Weather query parameters (lat/lon) | 0 seconds server-side — not logged |
| HTTP access logs | Disabled by default in skywatch config |

---

## 7. Security

- All HTTP communications use TLS in production
- No sensitive data is stored, minimising attack surface
- Dependencies are regularly audited via `pip-audit` and `npm audit`
- Contributions must not introduce tracking, analytics, or data collection

---

## 8. Children's Privacy

skywatch does not knowingly collect any data from children under 13 (COPPA) or under 16 (GDPR). The service collects no personal information at all.

---

## 9. Changes to This Policy

We will update this policy to reflect changes in skywatch's data practices. Material changes will be noted in the git commit history and CHANGELOG.

---

## 10. Contact

To report a privacy concern or request information, open an issue at:  
https://github.com/your-org/skywatch/issues

Label the issue `privacy`.
