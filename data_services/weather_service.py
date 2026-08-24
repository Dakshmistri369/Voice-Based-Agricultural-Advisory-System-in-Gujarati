"""
Open-Meteo Live Weather Forecast API Client & Gujarati Farming Advisory Rules Engine.
Supports all 33 Gujarat districts with 15-minute caching and offline fallback.
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import requests

from config import BASE_DIR

logger = logging.getLogger(__name__)


def get_weather_condition_gujarati(code: int) -> str:
    """Maps WMO Weather Interpretation Codes to Gujarati descriptions."""
    wmo_map = {
        0: "એકદમ ચોખ્ખું આકાશ",
        1: "મુખ્યત્વે ચોખ્ખું",
        2: "અંશતઃ વાદળછાયું",
        3: "વાદળછાયું આકાશ",
        45: "ઝાકળવાળું વાતાવરણ",
        48: "ઘાટા ઝાકળ વાતાવરણ",
        51: "હળવી બૂંદાબાંધી",
        53: "મધ્યમ બૂંદાબાંધી",
        55: "ભારે બૂંદાબાંધી",
        61: "હળવો વરસાદ",
        63: "મધ્યમ વરસાદ",
        65: "ભારે વરસાદ",
        80: "હળવા વરસાદના ઝાપટાં",
        81: "મધ્યમ વરસાદના ઝાપટાં",
        82: "મુસળધાર વરસાદ",
        95: "મેઘગર્જના સાથે વરસાદ"
    }
    return wmo_map.get(code, "સામાન્ય હવામાન")


class WeatherService:
    """Open-Meteo Weather Client with Gujarati Agricultural Advisory Engine."""

    def __init__(self, districts_path: Optional[Path] = None):
        self.districts_path = districts_path or (BASE_DIR / "data" / "districts_gujarat.json")
        self.districts = self._load_districts()
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl_seconds = 900  # 15 minutes cache

    def _load_districts(self) -> List[Dict[str, Any]]:
        """Loads 33 Gujarat districts reference table."""
        if not self.districts_path.exists():
            logger.warning(f"Districts file missing at {self.districts_path}.")
            return []
        try:
            with open(self.districts_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading districts: {e}")
            return []

    def _get_district_info(self, district_name: str) -> Dict[str, Any]:
        """Finds district lat/lon coordinates from name (Gujarati or English)."""
        clean_name = district_name.strip().lower()
        for d in self.districts:
            if (d["name_english"].lower() == clean_name or 
                d["name_gujarati"].lower() == clean_name or 
                clean_name in d["name_english"].lower()):
                return d

        # Default fallback to Rajkot
        return {
            "name_gujarati": "રાજકોટ",
            "name_english": "Rajkot",
            "lat": 22.3039,
            "lon": 70.8022
        }

    def fetch_weather(self, district_name: str = "Rajkot") -> Dict[str, Any]:
        """Fetches live current weather and forecast for any of the 33 Gujarat districts."""
        d_info = self._get_district_info(district_name)
        dist_key = d_info["name_english"]

        # Check cache
        now = time.time()
        if dist_key in self.cache:
            cached_data, cached_time = self.cache[dist_key]
            if now - cached_time < self.cache_ttl_seconds:
                return cached_data

        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": d_info["lat"],
            "longitude": d_info["lon"],
            "current_weather": "true",
            "hourly": "relativehumidity_2m",
            "daily": "weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max",
            "forecast_days": 5,
            "timezone": "Asia/Kolkata"
        }

        try:
            resp = requests.get(url, params=params, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                current = data.get("current_weather", {})
                daily = data.get("daily", {})

                temp_c = current.get("temperature", 32.0)
                wind_speed = current.get("windspeed", 12.0)
                code = current.get("weathercode", 0)
                condition_gu = get_weather_condition_gujarati(code)

                # Extract max humidity if available
                hourly_humidity = data.get("hourly", {}).get("relativehumidity_2m", [65])
                humidity = int(hourly_humidity[0]) if hourly_humidity else 65

                precip_sum = daily.get("precipitation_sum", [0.0])[0] if daily.get("precipitation_sum") else 0.0

                # Build 5-day forecast strip
                forecast_days = self._build_forecast_days(daily)

                # Generate Gujarati farming advisories
                advisories = self._generate_advisories(
                    temp_c=temp_c,
                    humidity=humidity,
                    wind_speed=wind_speed,
                    precip_mm=precip_sum,
                    code=code
                )

                res = {
                    "district_gujarati": d_info["name_gujarati"],
                    "district_english": d_info["name_english"],
                    "temp_c": temp_c,
                    "condition_gujarati": condition_gu,
                    "humidity": humidity,
                    "wind_speed": wind_speed,
                    "precipitation_mm": precip_sum,
                    "forecast_days": forecast_days,
                    "advisories": advisories,
                    "is_live": True,
                    "fetched_at": time.strftime("%Y-%m-%d %H:%M")
                }

                self.cache[dist_key] = (res, now)
                return res

        except Exception as e:
            logger.warning(f"Open-Meteo live API request failed: {e}. Returning cached fallback.")

        # Fallback response
        return self._get_fallback_weather(d_info)

    def _generate_advisories(
        self,
        temp_c: float,
        humidity: int,
        wind_speed: float,
        precip_mm: float,
        code: int
    ) -> List[str]:
        """Converts numeric weather metrics into actionable Gujarati agricultural advice."""
        advisories = []

        if precip_mm > 5.0 or code in [51, 53, 55, 61, 63, 65, 80, 81, 82, 95]:
            advisories.append("આવતીકાલે વરસાદની શક્યતા છે, તેથી જંતુનાશક દવા કે ખાતરનો છંટકાવ ટાળવો.")
        
        if temp_c > 37.0:
            advisories.append("અતિશય ગરમીને કારણે પાકને સાંજના સમયે પિયત આપવું અને જમીનમાં ભેજ જાળવવા મલ્ચિંગ કરવું.")
        
        if humidity > 78:
            advisories.append("હવામાં ભેજનું પ્રમાણ વધુ હોવાથી ફૂગજન્ય રોગ (ગેરુ/સુકારો) થવાની શક્યતા છે.")

        if wind_speed > 18.0:
            advisories.append("ઝડપી પવનને કારણે છંટકાવ કામગીરી મુલતવી રાખવી.")

        if not advisories:
            advisories.append("હવામાન પાક માટે અનુકૂળ છે, જરૂરિયાત મુજબ આંતરખેડ અને નિંદામણ કરવું.")

        return advisories

    def _build_forecast_days(self, daily: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Builds a 5-day list of {day_gu, temp_max, temp_min, rain_mm, rain_prob}."""
        import datetime
        GU_DAYS = ["સોમ", "મંગળ", "બુધ", "ગુરુ", "શુક્ર", "શનિ", "રવિ"]
        times      = daily.get("time", [])
        temp_max   = daily.get("temperature_2m_max", [])
        temp_min   = daily.get("temperature_2m_min", [])
        precip     = daily.get("precipitation_sum", [])
        rain_prob  = daily.get("precipitation_probability_max", [])
        result = []
        for i, dt_str in enumerate(times[:5]):
            try:
                dt = datetime.date.fromisoformat(dt_str)
                day_gu = GU_DAYS[dt.weekday()]
            except Exception:
                day_gu = "—"
            result.append({
                "day_gu":   day_gu,
                "temp_max": round(temp_max[i], 1) if i < len(temp_max) else "—",
                "temp_min": round(temp_min[i], 1) if i < len(temp_min) else "—",
                "rain_mm":  round(precip[i], 1)   if i < len(precip) else 0,
                "rain_prob":rain_prob[i]           if i < len(rain_prob) else 0,
            })
        return result

    def _get_fallback_weather(self, d_info: Dict[str, Any]) -> Dict[str, Any]:
        """Provides static weather advisory fallback when network fails."""
        return {
            "district_gujarati": d_info["name_gujarati"],
            "district_english": d_info["name_english"],
            "temp_c": 32.0,
            "condition_gujarati": "અંશતઃ વાદળછાયું",
            "humidity": 65,
            "wind_speed": 12.5,
            "precipitation_mm": 0.0,
            "forecast_days": [],
            "advisories": [
                "હવામાન સામાન્ય રહેવાની શક્યતા છે.",
                "પાકની જરૂરિયાત મુજબ પિયત આપવું અને નિંદામણ કરવું."
            ],
            "is_live": False,
            "fetched_at": time.strftime("%Y-%m-%d %H:%M")
        }


# Global singleton instance
weather_service = WeatherService()
