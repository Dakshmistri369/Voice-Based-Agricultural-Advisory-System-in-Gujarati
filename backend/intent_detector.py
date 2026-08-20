"""
intent_detector.py — Lightweight Gujarati + Hinglish intent classifier
No ML model needed; keyword matching covers ~90% of farmer queries accurately.
"""
from typing import Tuple

INTENT_KEYWORDS: dict[str, list[str]] = {
    "PRICE": [
        "ભાવ", "price", "rate", "daam", "dam", "mandi", "mandhi", "મંડી", "bazaar",
        "apmc", "bhav", "દર", "market price", "aaje", "today price",
        "kapas rate", "mungfali bhav", "jeera rate"
    ],
    "WEATHER": [
        "vaataavaran", "weather", "vatar", "varsad", "varsha", "rain", "baarish",
        "barish", "vaayu", "taapman", "taapmaan", "temperature", "aahvaa",
        "mausam", "forecast", "aavtu varsha", "vaadraa", "humidity", "aanev"
    ],
    "SCHEME": [
        "yojana", "scheme", "sahay", "subsidy", "madad", "help", "sarkar",
        "pm kisan", "pmkisan", "pmfby", "fasal bima", "kcc", "credit card",
        "atma", "mgnrega", "nrega", "kusum", "solar", "insurance", "vima",
        "application", "araji", "rupiya", "paisa", "benefit", "labh",
        "ikhedut", "gujarat scheme", "mukhyamantri", "CM scheme"
    ],
    "CROP_ADVICE": [
        "buvai", "sowing", "seed", "bij", "khatar", "khaatar", "fertilizer",
        "urea", "dap", "npk", "kheti", "fasal", "crop", "pani", "paani",
        "irrigation", "pest", "keeda", "disease", "dawai", "dava",
        "harvest", "katani", "variety", "jaath", "soil", "maati", "mitti"
    ],
    "DISEASE": [
        "rog", "disease", "bimari", "fungus", "keeda", "pest", "jassid",
        "bollworm", "aphid", "mite", "tikka", "blight", "wilt", "rot",
        "pila", "lal", "kaalo", "kaaloo", "patch", "symptoms", "lakshan"
    ],
}

# Order matters — first match wins
INTENT_ORDER = ["PRICE", "WEATHER", "SCHEME", "DISEASE", "CROP_ADVICE"]


def classify_intent(query: str) -> Tuple[str, float]:
    """
    Returns (intent, confidence).
    Checks each intent's keyword list; first match → confidence 0.95.
    Falls back to GENERAL with 0.4.
    """
    q = query.lower().strip()

    for intent in INTENT_ORDER:
        for kw in INTENT_KEYWORDS[intent]:
            if kw.lower() in q:
                return intent, 0.95

    return "GENERAL", 0.40


def extract_commodity(query: str) -> str | None:
    """Extract commodity name from a price-related query."""
    import json, pathlib
    prices_path = pathlib.Path(__file__).parent.parent / "data" / "prices" / "gujarat_prices.json"
    try:
        data = json.loads(prices_path.read_text(encoding="utf-8"))
        aliases: dict = data.get("commodity_aliases", {})
        q = query.lower()
        for alias, canonical in aliases.items():
            if alias in q:
                return canonical
    except Exception:
        pass
    return None


def extract_crop(query: str) -> str | None:
    """Extract crop key from a crop-advice query."""
    crop_map = {
        "kapas": "cotton", "cotton": "cotton",
        "mungfali": "groundnut", "groundnut": "groundnut",
        "erandi": "castor", "castor": "castor",
        "jeera": "cumin", "jiru": "cumin", "cumin": "cumin",
        "ghau": "wheat", "wheat": "wheat",
        "bajri": "bajra", "bajra": "bajra",
        "tuver": "tur", "tur": "tur", "toor": "tur",
        "makai": "maize", "maize": "maize",
        "dungali": "onion", "onion": "onion",
        "bateta": "potato", "potato": "potato",
        "tal": "sesame", "sesame": "sesame",
        "variyali": "fennel", "fennel": "fennel",
    }
    q = query.lower()
    for key, canonical in crop_map.items():
        if key in q:
            return canonical
    return None
