"""
Entity Extractor for Agricultural Entities (Crop, District, Commodity, Scheme).
"""

import re
from typing import Dict, Any, Optional

# Mapping of crops (Gujarati & Gujlish -> English Standard)
CROPS_MAP = {
    "કપાસ": "Cotton",
    "kapas": "Cotton",
    "cotton": "Cotton",
    "મગફળી": "Groundnut",
    "magfali": "Groundnut",
    "groundnut": "Groundnut",
    "જીરૂ": "Cumin",
    "jiru": "Cumin",
    "jeera": "Cumin",
    "cumin": "Cumin",
    "દીવેલા": "Castor",
    "divela": "Castor",
    "castor": "Castor",
    "ઘઉં": "Wheat",
    "ghau": "Wheat",
    "wheat": "Wheat",
    "ડુંગળી": "Onion",
    "dungri": "Onion",
    "onion": "Onion",
    "બટાટા": "Potato",
    "batata": "Potato",
    "potato": "Potato",
    "ડાંગર": "Paddy",
    "dangar": "Paddy",
    "paddy": "Paddy",
    "તલ": "Sesame",
    "tal": "Sesame",
    "sesame": "Sesame",
    "રાઈ": "Mustard",
    "rai": "Mustard",
    "mustard": "Mustard"
}

# 33 Gujarat Districts List (Gujarati & English)
GUJARAT_DISTRICTS = {
    "અમદાવાદ": "Ahmedabad",
    "ahmedabad": "Ahmedabad",
    "રાજકોટ": "Rajkot",
    "rajkot": "Rajkot",
    "જૂનાગઢ": "Junagadh",
    "junagadh": "Junagadh",
    "અમરેલી": "Amreli",
    "amreli": "Amreli",
    "સુરત": "Surat",
    "surat": "Surat",
    "વડોદરા": "Vadodara",
    "vadodara": "Vadodara",
    "જામનગર": "Jamnagar",
    "jamnagar": "Jamnagar",
    "ભાવનગર": "Bhavnagar",
    "bhavnagar": "Bhavnagar",
    "કચ્છ": "Kutch",
    "kutch": "Kutch",
    "કચ્છ-ભુજ": "Kutch",
    "મહેસાણા": "Mehsana",
    "mehsana": "Mehsana",
    "ગાંધીનગર": "Gandhinagar",
    "gandhinagar": "Gandhinagar",
    "બનાસકાંઠા": "Banaskantha",
    "banaskantha": "Banaskantha",
    "સાબરકાંઠા": "Sabarkantha",
    "sabarkantha": "Sabarkantha",
    "આણંદ": "Anand",
    "anand": "Anand",
    "ખેડા": "Kheda",
    "kheda": "Kheda",
    "મોરબી": "Morbi",
    "morbi": "Morbi",
    "પોરબંદર": "Porbandar",
    "porbandar": "Porbandar",
    "સુરેન્દ્રનગર": "Surendranagar",
    "surendranagar": "Surendranagar",
    "પાટણ": "Patan",
    "patan": "Patan",
    "ભરૂચ": "Bharuch",
    "bharuch": "Bharuch",
    "નવસારી": "Navsari",
    "navsari": "Navsari",
    "વલસાડ": "Valsad",
    "valsad": "Valsad",
    "તાપી": "Tapi",
    "tapi": "Tapi",
    "દાહોદ": "Dahod",
    "dahod": "Dahod",
    "પંચમહાલ": "Panchmahal",
    "panchmahal": "Panchmahal",
    "ડાંગ": "Dang",
    "dang": "Dang",
    "બોટાદ": "Botad",
    "botad": "Botad",
    "ગીર સોમનાથ": "Gir Somnath",
    "gir somnath": "Gir Somnath",
    "દેવભૂમિ દ્વારકા": "Devbhumi Dwarka",
    "dwarka": "Devbhumi Dwarka",
    "મહિસાગર": "Mahisagar",
    "mahisagar": "Mahisagar",
    "અરવલ્લી": "Aravalli",
    "aravalli": "Aravalli",
    "છોટા ઉદેપુર": "Chhota Udepur",
    "નર્મદા": "Narmada",
    "narmada": "Narmada"
}

# Recognized Schemes
SCHEMES_MAP = {
    "pm-kisan": "PM-KISAN",
    "pm kisan": "PM-KISAN",
    "પીએમ કિસાન": "PM-KISAN",
    "પીએમ-કિસાન": "PM-KISAN",
    "pmfby": "PMFBY",
    "પાક વીમો": "PMFBY",
    "pasal bima": "PMFBY",
    "ikhedut": "iKhedut",
    "ઇ-ખેડૂત": "iKhedut",
    "સોઇલ હેલ્થ કાર્ડ": "Soil Health Card",
    "soil health": "Soil Health Card",
    "kcc": "Kisan Credit Card",
    "કેસીસી": "Kisan Credit Card"
}


class EntityExtractor:
    """Extracts agricultural entities (crop, district, commodity, scheme) from query text."""

    def extract_entities(self, text: str) -> Dict[str, Optional[str]]:
        """Extracts recognized entities from user query."""
        clean_text = text.lower()

        extracted_crop = None
        extracted_district = None
        extracted_scheme = None

        # 1. Extract Crop
        for kw, crop_name in CROPS_MAP.items():
            if kw in clean_text:
                extracted_crop = crop_name
                break

        # 2. Extract District
        for kw, district_name in GUJARAT_DISTRICTS.items():
            if kw in clean_text:
                extracted_district = district_name
                break

        # Default district fallback to Rajkot / Ahmedabad if missing
        if not extracted_district:
            extracted_district = "Rajkot"

        # 3. Extract Scheme Name
        for kw, scheme_name in SCHEMES_MAP.items():
            if kw in clean_text:
                extracted_scheme = scheme_name
                break

        return {
            "crop": extracted_crop,
            "commodity": extracted_crop,  # AGMARKNET maps crop name directly
            "district": extracted_district,
            "district_gujarati": self._get_district_gujarati(extracted_district),
            "scheme_name": extracted_scheme,
        }

    def _get_district_gujarati(self, district_en: str) -> str:
        """Returns the Gujarati script name for an English district."""
        for gu, en in GUJARAT_DISTRICTS.items():
            if en.lower() == district_en.lower() and re.search(r"[\u0A80-\u0AFF]", gu):
                return gu
        return district_en


# Global singleton instance
entity_extractor = EntityExtractor()
