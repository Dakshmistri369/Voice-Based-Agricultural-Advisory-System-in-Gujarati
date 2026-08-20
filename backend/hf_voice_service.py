"""
hf_voice_service.py
-------------------
Wraps HuggingFace Inference API for:
  • STT → openai/whisper-large-v3  (HF_TOKEN_VOICE)
  • TTS → facebook/mms-tts-guj     (HF_TOKEN_VOICE)

Falls back gracefully if token is missing/API errors.
"""

import base64
import io
import logging
import uuid
from pathlib import Path

import httpx

from config import (
    HF_API_BASE,
    HF_STT_MODEL,
    HF_TTS_MODEL,
    HF_TOKEN_VOICE,
    AUDIO_DIR,
)

log = logging.getLogger(__name__)
_TIMEOUT = 60.0  # seconds


def _hf_headers() -> dict:
    return {"Authorization": f"Bearer {HF_TOKEN_VOICE}"}


# ──────────────────────────────────────────────────────────────
# STT  (audio bytes  →  Gujarati text)
# ──────────────────────────────────────────────────────────────

def transcribe_gujarati(audio_bytes: bytes, filename: str = "audio.webm") -> dict:
    """
    Send raw audio bytes to Whisper-large-v3 on HF.
    Returns {"text": str, "language": str, "error": str|None}
    """
    if not HF_TOKEN_VOICE:
        return {"text": "", "language": "gu", "error": "HF_TOKEN_VOICE not configured"}

    url = f"{HF_API_BASE}/{HF_STT_MODEL}"
    try:
        resp = httpx.post(
            url,
            headers={**_hf_headers(), "Content-Type": "audio/webm"},
            content=audio_bytes,
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        text = data.get("text", "").strip()
        log.info("STT result: %s", text[:80])
        return {"text": text, "language": "gu", "error": None}

    except httpx.HTTPStatusError as e:
        log.error("STT HTTP error %s: %s", e.response.status_code, e.response.text[:200])
        return {"text": "", "language": "gu", "error": str(e)}
    except Exception as e:
        log.error("STT error: %s", e)
        return {"text": "", "language": "gu", "error": str(e)}


# ──────────────────────────────────────────────────────────────
# TTS  (Gujarati text  →  WAV file path)
# ──────────────────────────────────────────────────────────────

def speak_gujarati(text: str) -> str | None:
    """
    Convert Gujarati text → audio via facebook/mms-tts-guj.
    Saves WAV to AUDIO_DIR and returns the filename (not full path).
    Returns None on failure (frontend falls back to SpeechSynthesis).
    """
    if not HF_TOKEN_VOICE:
        log.warning("HF_TOKEN_VOICE not set — TTS unavailable")
        return None

    # MMS-TTS expects plain JSON with "inputs" key
    url = f"{HF_API_BASE}/{HF_TTS_MODEL}"
    try:
        resp = httpx.post(
            url,
            headers={**_hf_headers(), "Content-Type": "application/json"},
            json={"inputs": text[:500]},   # API limit ~500 chars per call
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()

        # Response is raw audio bytes (audio/flac or audio/wav)
        audio_bytes = resp.content
        filename = f"{uuid.uuid4().hex}.wav"
        out_path: Path = AUDIO_DIR / filename
        out_path.write_bytes(audio_bytes)
        log.info("TTS saved: %s (%d bytes)", filename, len(audio_bytes))
        return filename

    except httpx.HTTPStatusError as e:
        log.error("TTS HTTP error %s: %s", e.response.status_code, e.response.text[:200])
        return None
    except Exception as e:
        log.error("TTS error: %s", e)
        return None
