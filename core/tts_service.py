"""
High-Performance Cascading Text-to-Speech (TTS) Engine for Gujarati Audio Generation.
Optimized for ultra-low latency (<0.5s), phonetic clarity, in-memory caching, and speech-text normalization.
"""

import io
import re
import os
import subprocess
import logging
from pathlib import Path
from typing import Tuple, Optional, Dict
import requests

try:
    from gtts import gTTS
except ImportError:
    gTTS = None

from config import settings, BASE_DIR

logger = logging.getLogger(__name__)


def clean_text_for_speech(text: str) -> str:
    """
    Normalizes text for natural Gujarati voice synthesis:
    Converts currency, units, technical acronyms to Gujarati phonetic words,
    and strips emojis, markdown asterisks, brackets, and URLs.
    """
    if not text:
        return ""

    t = text.strip()

    # 1. Remove markdown formatting & emojis
    t = re.sub(r"\*\*([^*]+)\*\*", r"\1", t)
    t = re.sub(r"\*([^*]+)\*", r"\1", t)
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)  # Markdown links
    t = re.sub(r"[🌾💰☔●◐⚠🌱🐛🌻🥜🌿🔬🧪💧⚙️✦🗑️🔍📄🏠]", "", t)

    # 2. Phonetic symbol & unit replacements in Gujarati
    t = t.replace("₹", " રૂપિયા ")
    t = t.replace("Rs.", " રૂપિયા ").replace("Rs", " રૂપિયા ")
    t = re.sub(r"(\d+)\s*kg", r"\1 કિલો", t, flags=re.IGNORECASE)
    t = re.sub(r"(\d+)\s*°C", r"\1 ડિગ્રી સેલ્સિયસ", t, flags=re.IGNORECASE)
    t = re.sub(r"(\d+)\s*%", r"\1 ટકા", t)
    t = t.replace("APMC", "એપીએમસી")
    t = t.replace("PM-KISAN", "પીએમ કિસાન")
    t = t.replace("PMFBY", "પીએમ ફસલ બીમા")
    t = t.replace("KVK", "કૃષિ વિજ્ઞાન કેન્દ્ર")
    t = t.replace("Rajkot", "રાજકોટ")
    t = t.replace("Ahmedabad", "અમદાવાદ")
    t = t.replace("Surat", "સુરત")
    t = t.replace("Vadodara", "વડોદરા")
    t = t.replace("Junagadh", "જૂનાગઢ")
    t = t.replace("Amreli", "અમરેલી")
    t = t.replace("Bhavnagar", "ભાવનગર")
    t = t.replace("Jamnagar", "જામનગર")
    t = t.replace("Kutch", "કચ્છ")
    t = t.replace("Mehsana", "મહેસાણા")
    t = t.replace("Gandhinagar", "ગાંધીનગર")
    t = t.replace("Cotton", "કપાસ")
    t = t.replace("Groundnut", "મગફળી")
    t = t.replace("Wheat", "ઘઉં")
    t = t.replace("Cumin", "જીરું")
    t = t.replace("Castor", "એરંડા")
    t = t.replace("Onion", "ડુંગળી")
    t = t.replace("Bajra", "બાજરી")
    t = t.replace("Sesame", "તલ")

    # 3. Clean up parenthesized notes for smoother speech
    t = re.sub(r"\(ન્યૂનતમ:\s*₹?(\d+),\s*મહત્તમ:\s*₹?(\d+)\)", r"જેમાં ઓછામાં ઓછો ભાવ રૂપિયા \1 અને વધુમાં વધુ ભાવ રૂપિયા \2 રહ્યો છે.", t)
    t = re.sub(r"[\(\)\[\]\{\}]", " ", t)

    # 4. Clean extra spaces
    t = re.sub(r"\s+", " ", t).strip()
    return t


def detect_audio_mime_type(audio_bytes: bytes) -> str:
    """Returns correct MIME type (audio/wav or audio/mp3) based on file magic bytes."""
    if not audio_bytes:
        return "audio/mp3"
    if audio_bytes.startswith(b"RIFF"):
        return "audio/wav"
    return "audio/mp3"


class TTSService:
    """Low-latency Gujarati TTS service with in-memory caching and resilient audio fallback."""

    def __init__(self):
        self.piper_model_dir = BASE_DIR / "models" / "piper"
        self.piper_onnx = self.piper_model_dir / "gu_IN-cpm-medium.onnx"
        self._cache: Dict[str, bytes] = {}
        self._max_cache_size = 200

    def synthesize_speech(self, gujarati_text: str) -> Tuple[bytes, str]:
        """
        Synthesizes Gujarati text into audio bytes with caching and fast response.
        Returns: (audio_bytes: bytes, engine_name: str)
        """
        raw_text = gujarati_text.strip()
        if not raw_text:
            return b"", "None"

        clean_text = clean_text_for_speech(raw_text)
        if not clean_text:
            clean_text = raw_text

        # ── 1. Check In-Memory Cache (Instant 0ms) ───────────
        if clean_text in self._cache:
            return self._cache[clean_text], "Cached Audio"

        # ── 2. Priority 1: Piper Local ONNX (if local model installed)
        if self.piper_onnx.exists():
            try:
                audio_bytes = self._synthesize_piper_local(clean_text)
                if audio_bytes and len(audio_bytes) > 200:
                    self._add_to_cache(clean_text, audio_bytes)
                    return audio_bytes, "Piper TTS (Local ONNX gu_IN)"
            except Exception as e:
                logger.warning(f"Local Piper ONNX synthesis failed: {e}")

        # ── 3. Priority 2: gTTS with Indian server (High-quality, reliable, fast ~0.5s)
        if gTTS is not None:
            try:
                audio_bytes = self._synthesize_gtts(clean_text)
                if audio_bytes and len(audio_bytes) > 200:
                    self._add_to_cache(clean_text, audio_bytes)
                    return audio_bytes, "gTTS (Gujarati High Quality)"
            except Exception as e:
                logger.warning(f"gTTS synthesis failed: {e}")

        # ── 4. Priority 3: Hugging Face Inference Fallback (1.5s max timeout)
        if settings.HF_API_KEY:
            try:
                audio_bytes = self._synthesize_hf_mms_tts(clean_text)
                if audio_bytes and len(audio_bytes) > 200:
                    self._add_to_cache(clean_text, audio_bytes)
                    return audio_bytes, "HF MMS-TTS (facebook/mms-tts-guj)"
            except Exception as e:
                logger.warning(f"HF MMS-TTS synthesis failed: {e}")

        logger.error("All TTS engines failed or unavailable.")
        return b"", "TTS Unavailable"

    def _add_to_cache(self, key: str, audio: bytes):
        """Adds audio to cache, keeping cache within max size."""
        if len(self._cache) >= self._max_cache_size:
            first_key = next(iter(self._cache))
            del self._cache[first_key]
        self._cache[key] = audio

    def _synthesize_gtts(self, text: str) -> Optional[bytes]:
        """Generates audio via gTTS using Indian TLD for lowest latency."""
        # Synthesize up to first 250 characters for immediate spoken feedback
        speech_slice = text[:250].strip()
        tts = gTTS(text=speech_slice, lang="gu", tld="co.in", timeout=3.0)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()

    def _synthesize_piper_local(self, text: str) -> Optional[bytes]:
        """Synthesizes audio using Piper ONNX binary/subprocess."""
        output_wav = self.piper_model_dir / "temp_output.wav"
        cmd = [
            "piper",
            "--model", str(self.piper_onnx),
            "--output_file", str(output_wav)
        ]
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, _ = process.communicate(input=text.encode("utf-8"), timeout=3)

        if output_wav.exists():
            with open(output_wav, "rb") as f:
                data = f.read()
            output_wav.unlink(missing_ok=True)
            return data
        return None

    def _synthesize_hf_mms_tts(self, text: str) -> Optional[bytes]:
        """Queries HF Inference API for facebook/mms-tts-guj with strict 1.5s timeout."""
        api_url = "https://api-inference.huggingface.co/models/facebook/mms-tts-guj"
        headers = {"Authorization": f"Bearer {settings.HF_API_KEY}"}
        payload = {"inputs": text[:200]}

        resp = requests.post(api_url, headers=headers, json=payload, timeout=1.5)
        if resp.status_code == 200 and len(resp.content) > 100:
            return resp.content
        return None


# Global singleton instance
tts_service = TTSService()
