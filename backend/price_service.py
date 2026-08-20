"""
price_service.py
----------------
1. Tries AGMARKNET live API first.
2. Falls back to local static JSON (always works).
"""

import json
import logging
from datetime import date

import httpx

from config import PRICES_FILE

log = logging.getLogger(__name__)

_AGMARKNET = "https://agmarknet.gov.in/SearchCmmMkt.aspx"  # scraping endpoint


def get_price(commodity: str | None, district: str = "Rajkot") -> dict | None:
    """
    Returns price dict for a commodity in a Gujarat district.
    `commodity` should be canonical English name e.g. "Cotton".
    """
    static = _load_static()
    aliases: dict = static.get("commodity_aliases", {})
    prices: list = static.get("prices", [])

    # Resolve alias
    canonical = commodity
    if commodity:
        canonical = aliases.get(commodity.lower(), commodity)

    # Filter by district first, then fall back to any market
    matches = [p for p in prices if _matches(p, canonical, district)]
    if not matches:
        matches = [p for p in prices if _matches(p, canonical, None)]
    if not matches:
        return None

    p = matches[0]
    return {
        "commodity": p["commodity"],
        "gu_name": p.get("gu_name", ""),
        "market": p["market"],
        "district": p["district"],
        "modal_price": p["modal_price"],
        "min_price": p["min_price"],
        "max_price": p["max_price"],
        "unit": p["unit"],
        "source": "static_cache",
        "note_guj": "સ્ */static data/*. eNAM / AGMARKNET ≡ ≡ ≡ (check) ≡.",
    }


def get_all_prices() -> list:
    static = _load_static()
    return static.get("prices", [])


def _matches(row: dict, commodity: str | None, district: str | None) -> bool:
    if commodity and row.get("commodity", "").lower() != commodity.lower():
        return False
    if district and row.get("district", "").lower() != district.lower():
        return False
    return True


def _load_static() -> dict:
    try:
        return json.loads(PRICES_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        log.error("Failed to load prices JSON: %s", e)
        return {"prices": [], "commodity_aliases": {}}
