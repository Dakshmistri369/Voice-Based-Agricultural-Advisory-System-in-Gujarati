"""
Transliterator & Normalizer for Romanised Gujlish to Gujarati Script.
Preserves agricultural proper nouns (PM-KISAN, NPK, urea, APMC, KVK) untouched.
"""

import re
from typing import Dict

# Dictionary mapping common Gujlish phrases to Gujarati script
GUJLISH_PHRASE_MAP: Dict[str, str] = {
    "aaje": "આજે",
    "aavtikale": "આવતીકાલે",
    "bhav": "ભાવ",
    "bajar bhav": "બજાર ભાવ",
    "kapas": "કપાસ",
    "magfali": "મગફળી",
    "jiru": "જીરૂ",
    "divela": "દીવેલા",
    "ghau": "ઘઉં",
    "khatar": "ખાતર", "dose": "ડોઝ",
    "varsad": "વરસાદ",
    "havaman": "હવામાન",
    "tampman": "તાપમાન",
    "paisa": "પૈસા",
    "male": "મળે",
    "male che": "મળે છે",
    "kitla": "કેટલા",
    "yojana": "યોજના",
    "sahay": "સહાય",
    "dava": "દવા",
    "rog": "રોગ",
    "vavetar": "વાવેતર",
    "biyaran": "બિયારણ",
    "sinchai": "સિંચાઈ"
}

# Preserve acronyms and proper nouns
PROPER_NOUNS = ["PM-KISAN", "PMFBY", "NPK", "UREA", "DAP", "APMC", "KVK", "ATMA", "iKhedut"]


class GujlishTransliterator:
    """Normalizes Romanised Gujlish text into Gujarati script."""

    def normalize_text(self, text: str) -> str:
        """Converts Gujlish words to Gujarati script while preserving proper nouns."""
        if not text:
            return ""

        words = text.split()
        normalized_words = []

        for word in words:
            clean_word = word.strip(",.!?")
            # Preserve proper nouns uppercase
            if clean_word.upper() in PROPER_NOUNS:
                normalized_words.append(clean_word.upper())
                continue

            # Convert Gujlish phrase
            lower_word = clean_word.lower()
            if lower_word in GUJLISH_PHRASE_MAP:
                normalized_words.append(GUJLISH_PHRASE_MAP[lower_word])
            else:
                normalized_words.append(word)

        return " ".join(normalized_words)


# Global singleton instance
transliterator = GujlishTransliterator()
