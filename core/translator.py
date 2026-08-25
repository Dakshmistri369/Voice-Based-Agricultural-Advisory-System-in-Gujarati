"""
Bidirectional Gujarati ↔ English Translation Layer with In-Memory Caching.
Uses deep-translator (Google Translate engine) with HF API and offline dictionary fallback.
"""

import logging
from typing import Dict, Optional
import requests

from config import settings

logger = logging.getLogger(__name__)

# Basic fallback translation mapping dictionary for offline testing
FALLBACK_GU_TO_EN: Dict[str, str] = {
    "કપાસ માટે કેટલું ખાતર નાખવું?": "How much fertilizer to apply for cotton?",
    "PM-KISAN યોજનામાં કેટલા રૂપિયા મળે છે?": "How much money is given in PM-KISAN scheme?",
    "આજે કપાસનો બજાર ભાવ કેટલો છે?": "What is today's market price of cotton?",
    "આવતીકાલે વરસાદ પડશે?": "Will it rain tomorrow?",
    "મગફળીમાં વાવેતર નો સમય ક્યારે?": "When is the sowing time for groundnut?",
    "કપાસ માં ખાતર નો ડોઝ કેટલો": "What is the fertilizer dosage for cotton?",
    "પાંદડા પર ગેરુ નો રોગ થયો છે": "There is a rust disease on leaves",
    "નમસ્તે કિસાન મિત્ર": "Hello farmer friend",
    "ખેતરની માટી ક્યારે ખેડવી?": "When should farm soil be ploughed?",
}

FALLBACK_EN_TO_GU: Dict[str, str] = {
    "Under the PM-KISAN scheme, eligible farmers receive Rs 6,000 per year in three installments.": "પીએમ-કિસાન યોજના હેઠળ તમામ પાત્ર ખેડૂતોને વાર્ષિક ₹6,000 ત્રણ હપ્તામાં મળે છે.",
    "Apply 240 kg Nitrogen per hectare for cotton crop in 3 split doses.": "કપાસમાં હેક્ટર દીઠ 240 કિલો નાઇટ્રોજન 3 હપ્તામાં આપવું.",
    "Light rain is expected tomorrow. Avoid spraying pesticides.": "આવતીકાલે હળવો વરસાદ પડી શકે છે. દવા નો છંટકાવ ટાળવો."
}


class TranslatorService:
    """Translation Service for gu ↔ en pivoting with LRU cache and multi-tier fallbacks."""

    def __init__(self):
        self.cache: Dict[str, str] = {}
        self._deep_translator_gu2en = None
        self._deep_translator_en2gu = None

        try:
            from deep_translator import GoogleTranslator
            self._deep_translator_gu2en = GoogleTranslator(source='gu', target='en')
            self._deep_translator_en2gu = GoogleTranslator(source='en', target='gu')
            logger.info("deep-translator initialized successfully.")
        except Exception as e:
            logger.warning(f"Could not initialize deep-translator: {e}")

    def translate_gu_to_en(self, gujarati_text: str) -> str:
        """Translates Gujarati query to English for intent classification & RAG search."""
        text = gujarati_text.strip()
        if not text:
            return ""

        # Check Cache
        cache_key = f"gu2en:{text}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # 1. Check offline fallback dictionary
        if text in FALLBACK_GU_TO_EN:
            res = FALLBACK_GU_TO_EN[text]
            self.cache[cache_key] = res
            return res

        # 2. Try deep_translator (fast, robust, free)
        if self._deep_translator_gu2en:
            try:
                translated = self._deep_translator_gu2en.translate(text)
                if translated and translated.strip():
                    self.cache[cache_key] = translated.strip()
                    return translated.strip()
            except Exception as e:
                logger.warning(f"deep-translator gu->en error: {e}")

        # 3. Call HF NLLB-200 / IndicTrans2 Inference API if key configured
        if settings.HF_API_KEY:
            try:
                translated = self._call_hf_translation_api(text, src_lang="guj_Gujr", tgt_lang="eng_Latn")
                if translated:
                    self.cache[cache_key] = translated
                    return translated
            except Exception as e:
                logger.warning(f"HF Translation API gu->en failed: {e}")

        # 4. Fallback: return original text
        self.cache[cache_key] = text
        return text

    def translate_en_to_gu(self, english_text: str) -> str:
        """Translates English LLM answer into natural Gujarati."""
        text = english_text.strip()
        if not text:
            return ""

        cache_key = f"en2gu:{text}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # 1. Check dictionary
        if text in FALLBACK_EN_TO_GU:
            res = FALLBACK_EN_TO_GU[text]
            self.cache[cache_key] = res
            return res

        # 2. Try deep_translator
        if self._deep_translator_en2gu:
            try:
                translated = self._deep_translator_en2gu.translate(text)
                if translated and translated.strip():
                    self.cache[cache_key] = translated.strip()
                    return translated.strip()
            except Exception as e:
                logger.warning(f"deep-translator en->gu error: {e}")

        # 3. Try HF API
        if settings.HF_API_KEY:
            try:
                translated = self._call_hf_translation_api(text, src_lang="eng_Latn", tgt_lang="guj_Gujr")
                if translated:
                    self.cache[cache_key] = translated
                    return translated
            except Exception as e:
                logger.warning(f"HF Translation API en->gu failed: {e}")

        self.cache[cache_key] = text
        return text

    def _call_hf_translation_api(self, text: str, src_lang: str, tgt_lang: str) -> Optional[str]:
        """Queries Hugging Face NLLB-200 Inference Endpoint."""
        api_url = f"https://api-inference.huggingface.co/models/{settings.TRANSLATION_MODEL_ID}"
        headers = {"Authorization": f"Bearer {settings.HF_API_KEY}"}
        payload = {
            "inputs": text,
            "parameters": {"src_lang": src_lang, "tgt_lang": tgt_lang}
        }

        resp = requests.post(api_url, headers=headers, json=payload, timeout=1.5)
        if resp.status_code == 200:
            res_json = resp.json()
            if isinstance(res_json, list) and len(res_json) > 0:
                return res_json[0].get("translation_text", text)

        return None


# Global singleton instance
translator_service = TranslatorService()
