"""
Open-Meteo Air Quality Index (AQI) Service for Gujarati Kisaan Mitra AI.
Uses the free Open-Meteo Air Quality API — no API key required.
"""

import logging
import requests
from typing import Dict, Any, Optional

from config import BASE_DIR

logger = logging.getLogger(__name__)

AQI_API_BASE = "https://air-quality-api.open-meteo.com/v1/air-quality"

AQI_BUCKETS = [
    (50,  "સારી (Good)",              "બહાર કામ કરવા માટે સલામત.",                  "aqi-good"),
    (100, "મધ્યમ (Moderate)",          "સંવેદનશીલ વ્યક્તિઓ સાવધાન રહે.",            "aqi-moderate"),
    (150, "અસ્વસ્થ (Sensitive)",        "લાંબો સમય બહાર કામ ટાળો.",                  "aqi-unhealthy"),
    (200, "અસ્વસ્થ (Unhealthy)",        "માસ્ક પહેરો, ખેતરમાં કામ ઓછું કરો.",         "aqi-unhealthy"),
    (999, "ખતરનાક (Hazardous)",        "શક્ય હોય ત્યાં સુધી ઘરની અંદર રહો.",         "aqi-hazardous"),
]

FARMING_AQI_ADVICE = {
    "aqi-good":      "🌾 આ AQI સ્તરે ખુલ્લામાં ખેત-કાર્ય (સ્પ્રે, લણણી) સલામત.",
    "aqi-moderate":  "⚠️ સ્પ્રે કાર્ય સવારે વહેલું કે સાંજે મોડું કરો.",
    "aqi-unhealthy": "⚠️ ખેતરમાં દીર્ઘ સ્પ્રે / ખેત-મજૂરી ટાળો. N95 માસ્ક વાપરો.",
    "aqi-hazardous": "🚫 ખેત-મજૂરી/સ્પ્રે-ઓ કામ સ્થગિત કરો. ઘરની અંદર રહો.",
}


def get_district_coords(district_name: str):
    """Returns (lat, lon) for a district name from districts_gujarat.json."""
    import json
    data_path = BASE_DIR / "data" / "districts_gujarat.json"
    try:
        with open(data_path, encoding="utf-8") as f:
            data = json.load(f)
        for d in data:
            if (d.get("name_gujarati", "") == district_name or
                    d.get("name_english", "").lower() == district_name.lower()):
                return d["lat"], d["lon"]
    except Exception:
        pass
    return 22.3, 70.8  # Default: Rajkot


def fetch_aqi(district_name: str) -> Dict[str, Any]:
    """
    Fetches live AQI for the given Gujarat district from Open-Meteo Air Quality API.
    Returns a structured dict with AQI value, bucket label, advisory, and farming advice.
    """
    lat, lon = get_district_coords(district_name)

    try:
        resp = requests.get(
            AQI_API_BASE,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "pm10,pm2_5,us_aqi,european_aqi,ozone,carbon_monoxide,nitrogen_dioxide"
            },
            timeout=6
        )
        if resp.status_code == 200:
            data = resp.json()
            current = data.get("current", {})
            us_aqi = current.get("us_aqi", 0) or 0
            pm25 = current.get("pm2_5", 0) or 0
            pm10 = current.get("pm10", 0) or 0

            bucket_label, bucket_advice, bucket_class = _classify_aqi(us_aqi)
            return {
                "us_aqi": round(us_aqi),
                "pm25": round(pm25, 1),
                "pm10": round(pm10, 1),
                "bucket_label": bucket_label,
                "bucket_advice": bucket_advice,
                "bucket_class": bucket_class,
                "farming_advice": FARMING_AQI_ADVICE.get(bucket_class, ""),
                "is_live": True
            }
    except Exception as e:
        logger.warning(f"AQI API fetch failed for {district_name}: {e}")

    # Fallback: safe default
    return {
        "us_aqi": 45,
        "pm25": 12.0,
        "pm10": 25.0,
        "bucket_label": "સારી (Good)",
        "bucket_advice": "બહાર કામ કરવા માટે સલામત.",
        "bucket_class": "aqi-good",
        "farming_advice": FARMING_AQI_ADVICE["aqi-good"],
        "is_live": False
    }


def _classify_aqi(aqi_value: float):
    for threshold, label, advice, css_class in AQI_BUCKETS:
        if aqi_value <= threshold:
            return label, advice, css_class
    return AQI_BUCKETS[-1][1], AQI_BUCKETS[-1][2], AQI_BUCKETS[-1][3]
