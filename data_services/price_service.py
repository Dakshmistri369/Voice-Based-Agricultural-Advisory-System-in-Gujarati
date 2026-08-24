"""
AGMARKNET Live APMC Mandi Price Service with Cached Snapshot Fallback.
Fetches today's commodity market prices for Gujarat districts.
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional
import requests

from config import settings, BASE_DIR

logger = logging.getLogger(__name__)


class PriceService:
    """AGMARKNET APMC Price Client with offline JSON fallback cache."""

    def __init__(
        self,
        commodity_map_path: Optional[Path] = None,
        cache_path: Optional[Path] = None
    ):
        self.commodity_map_path = commodity_map_path or (BASE_DIR / "data" / "commodity_map.json")
        self.cache_path = cache_path or (BASE_DIR / "data" / "mandi_price_cache.json")
        self.commodity_map = self._load_json(self.commodity_map_path)
        self.price_cache = self._load_json(self.cache_path)

    def _load_json(self, path: Path) -> Dict[str, Any]:
        """Loads JSON file helper."""
        if not path.exists():
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {path.name}: {e}")
            return {}

    def fetch_mandi_price(
        self,
        commodity_name: str = "Cotton",
        district_name: str = "Rajkot"
    ) -> Dict[str, Any]:
        """
        Fetches today's APMC mandi price for a commodity in a Gujarat district.
        Returns: {commodity_gu, commodity_en, modal_price, min_price, max_price, district_gu, price_date, is_live}
        """
        # Resolve Commodity Metadata
        commodity_info = self._resolve_commodity_info(commodity_name)
        comm_key = commodity_info["name_english"]
        dist_key = district_name.capitalize()

        # Try Live AGMARKNET API if API key is configured
        if settings.DATA_GOV_IN_API_KEY:
            live_data = self._fetch_agmarknet_live(
                commodity_agmarknet=commodity_info["agmarknet_name"],
                district=dist_key
            )
            if live_data:
                live_data["commodity_gu"] = commodity_info["name_gujarati"]
                live_data["commodity_en"] = commodity_info["name_english"]
                live_data["is_live"] = True
                return live_data

        # Fallback to Cached Snapshot
        return self._get_cached_price(comm_key, dist_key, commodity_info)

    def _resolve_commodity_info(self, query_comm: str) -> Dict[str, str]:
        """Resolves commodity string (Gujarati or English) to standard metadata."""
        clean = query_comm.strip().lower()

        for key, meta in self.commodity_map.items():
            if (key.lower() == clean or 
                meta["name_gujarati"].lower() == clean or 
                clean in meta["name_gujarati"].lower() or 
                clean in key.lower()):
                return meta

        # Default Cotton
        return self.commodity_map.get(
            "Cotton",
            {
                "name_gujarati": "કપાસ",
                "name_english": "Cotton",
                "agmarknet_name": "Cotton",
                "unit": "20 kg"
            }
        )

    def _fetch_agmarknet_live(
        self,
        commodity_agmarknet: str,
        district: str
    ) -> Optional[Dict[str, Any]]:
        """Queries data.gov.in AGMARKNET live resource API."""
        resource_id = "9ef0be3f-08b4-4318-a2f9-2b70dcd99853"
        url = f"https://api.data.gov.in/resource/{resource_id}"

        params = {
            "api-key": settings.DATA_GOV_IN_API_KEY,
            "format": "json",
            "filters[state]": "Gujarat",
            "filters[district]": district,
            "filters[commodity]": commodity_agmarknet,
            "limit": 1
        }

        try:
            resp = requests.get(url, params=params, timeout=5)
            if resp.status_code == 200:
                records = resp.json().get("records", [])
                if records:
                    rec = records[0]
                    return {
                        "district_gu": district,
                        "market_name": rec.get("market", district),
                        "modal_price": int(rec.get("modal_price", 1500)),
                        "min_price": int(rec.get("min_price", 1400)),
                        "max_price": int(rec.get("max_price", 1600)),
                        "unit": "20 kg",
                        "price_date": rec.get("arrival_date", time.strftime("%Y-%m-%d")),
                    }
        except Exception as e:
            logger.warning(f"AGMARKNET API fetch failed: {e}")

        return None

    def _get_cached_price(
        self,
        comm_key: str,
        dist_key: str,
        commodity_info: Dict[str, str]
    ) -> Dict[str, Any]:
        """Provides snapshot cached mandi prices."""
        dist_cache = self.price_cache.get(dist_key, self.price_cache.get("Rajkot", {}))
        comm_cache = dist_cache.get(
            comm_key,
            {"modal_price": 1550, "min_price": 1480, "max_price": 1620, "date": "2026-08-21"}
        )

        return {
            "commodity_gu": commodity_info["name_gujarati"],
            "commodity_en": commodity_info["name_english"],
            "district_gu": dist_key,
            "market_name": f"{dist_key} APMC",
            "modal_price": comm_cache["modal_price"],
            "min_price": comm_cache["min_price"],
            "max_price": comm_cache["max_price"],
            "unit": commodity_info.get("unit", "20 kg"),
            "price_date": comm_cache.get("date", "2026-08-21"),
            "is_live": False
        }


# Global singleton instance
price_service = PriceService()
