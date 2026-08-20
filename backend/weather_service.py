"""
weather_service.py
------------------
Fetches weather from Open-Meteo (free, no API key).
Generates Gujarati farming advisories from the data.
Caches last response to disk for offline fallback.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

import httpx

from config import DEFAULT_LAT, DEFAULT_LON, DEFAULT_CITY, WEATHER_CACHE

log = logging.getLogger(__name__)

OPEN_METEO_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude={lat}&longitude={lon}"
    "&current=temperature_2m,relative_humidity_2m,precipitation,weathercode,windspeed_10m"
    "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode"
    "&timezone=Asia%2FKolkata&forecast_days=5"
)

WMO_CODES = {
    0: "સ્પષ્ટ આકાશ ☀️",
    1: "મુખ્યત્વે સ્પષ્ટ 🌤️",
    2: "અંશતઃ વાદળછ ☁️",
    3: "વાદળછ 🌧️",
    45: "ધુ. (Fog) 🌫️",
    51: "ઝ. ઝ. (Drizzle) 🌦️",
    61: "ह. (Light rain) 🌧️",
    63: "ম. (Moderate rain) 🌧️",
    65: "ভ. (Heavy rain) ⛈️",
    80: "ড. (Rain showers) 🌦️",
    95: "ব. (Thunderstorm) ⛈️",
}


def get_weather_advisory(lat: float = DEFAULT_LAT, lon: float = DEFAULT_LON, city: str = DEFAULT_CITY) -> dict:
    url = OPEN_METEO_URL.format(lat=lat, lon=lon)
    try:
        resp = httpx.get(url, timeout=8.0)
        resp.raise_for_status()
        raw = resp.json()
        result = _parse(raw, city)
        # cache for offline
        WEATHER_CACHE.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
        result["source"] = "live"
        return result
    except Exception as e:
        log.warning("Weather API failed (%s), using cache", e)
        return _read_cache(city)


def _parse(raw: dict, city: str) -> dict:
    cur = raw.get("current", {})
    daily = raw.get("daily", {})

    temp = cur.get("temperature_2m", 0)
    humidity = cur.get("relative_humidity_2m", 0)
    rain_now = cur.get("precipitation", 0) > 0
    wind = cur.get("windspeed_10m", 0)
    wcode = cur.get("weathercode", 0)

    advisories = _make_advisories(temp, humidity, rain_now, daily)

    forecast = []
    dates = daily.get("time", [])
    for i, d in enumerate(dates[:5]):
        forecast.append({
            "date": d,
            "max_temp": daily["temperature_2m_max"][i],
            "min_temp": daily["temperature_2m_min"][i],
            "rain_mm": daily["precipitation_sum"][i],
            "condition": WMO_CODES.get(daily["weathercode"][i], "—"),
        })

    return {
        "city": city,
        "current_temp": f"{temp}°C",
        "humidity": f"{humidity}%",
        "wind_kmh": f"{wind} km/h",
        "condition": WMO_CODES.get(wcode, "—"),
        "rain_today": "હા 🌧️" if rain_now else "ના ☀️",
        "forecast_days": forecast,
        "advisories": advisories,
        "fetched_at": datetime.now().strftime("%d-%m-%Y %H:%M"),
    }


def _make_advisories(temp: float, humidity: float, rain_now: bool, daily: dict) -> list:
    ads = []
    rain_5d = daily.get("precipitation_sum", [0] * 5)

    if rain_now or (rain_5d and rain_5d[0] > 5):
        ads.append({
            "type": "RAINFALL",
            "icon": "🌧️",
            "msg_guj": "આજે/આ. (today) વ. (rain) → ખ. (fertilizer/pesticide) ઉ.ઉ. (don't apply). Drainage ч. (check) ч.",
        })
    if humidity > 80 and not rain_now:
        ads.append({
            "type": "HIGH_HUMIDITY",
            "icon": "💧",
            "msg_guj": f"Humidity {humidity}% — ফ. (fungal disease) ≡ risk. ח. (fungicide) ч. ≡ (apply preventively).",
        })
    if temp > 38:
        ads.append({
            "type": "HEATWAVE",
            "icon": "🌡️",
            "msg_guj": f"Temp {temp}°C — ≡ (mulching) + ≡ (more water). ≡ (animals) ≡ ≡ (shade + water).",
        })
    if temp < 10:
        ads.append({
            "type": "COLD",
            "icon": "❄️",
            "msg_guj": f"Temp {temp}°C — ≡ (frost risk). ≡ (wheat/rabi crops) ≡ ≡ (protect). ≡ (light irrigation) ≡.",
        })
    if not ads:
        ads.append({
            "type": "OK",
            "icon": "✅",
            "msg_guj": "≡ (weather OK). ≡ (normal farming) ≡ (continue).",
        })
    return ads


def _read_cache(city: str) -> dict:
    try:
        data = json.loads(WEATHER_CACHE.read_text(encoding="utf-8"))
        data["source"] = "cache"
        return data
    except Exception:
        return {
            "city": city, "current_temp": "N/A", "humidity": "N/A",
            "rain_today": "N/A", "forecast_days": [], "advisories": [],
            "source": "unavailable",
        }
