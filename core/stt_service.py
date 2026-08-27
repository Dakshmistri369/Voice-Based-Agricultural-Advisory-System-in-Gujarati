"""
Speech-to-Text (STT) Service Wrapper supporting Google Speech Recognition (gu-IN, hi-IN, en-IN),
Whisper (HF API & Local), and Vosk Gujarati.
"""

import io
import os
import logging
from pathlib import Path
from typing import Tuple, Optional
import requests

try:
    import speech_recognition as sr
except ImportError:
    sr = None

from config import settings, BASE_DIR
from core.audio_utils import normalize_audio_to_wav

logger = logging.getLogger(__name__)


class STTService:
    """Unified Speech-to-Text Interface for Gujarati Voice Input."""

    def __init__(self, mode: str = settings.STT_MODE):
        self.mode = mode
        self.vosk_model_dir = BASE_DIR / "models" / "vosk" / "vosk-model-small-gu-0.42"
        self._recognizer = sr.Recognizer() if sr is not None else None
        if self._recognizer is not None:
            self._recognizer.energy_threshold = 300
            self._recognizer.dynamic_energy_threshold = True

    def transcribe_audio(self, audio_bytes: bytes) -> Tuple[str, str]:
        """
        Transcribes audio bytes into Gujarati text.
        Returns: (transcript: str, engine_name: str)
        """
        if not audio_bytes or len(audio_bytes) < 100:
            return "", "None"

        # Normalize arbitrary browser audio (WebM/Opus/Ogg/MP3/WAV) to 16kHz Mono WAV
        wav_bytes = normalize_audio_to_wav(audio_bytes)
        if not wav_bytes or len(wav_bytes) < 100:
            return "", "None"

        # ── 1. Priority 1: Google Speech Recognition (gu-IN, hi-IN, en-IN)
        if self._recognizer is not None:
            try:
                transcript = self._transcribe_google_speech(wav_bytes)
                if transcript and transcript.strip():
                    return transcript.strip(), "Google Speech Recognition (gu-IN)"
            except Exception as e:
                logger.warning(f"Google Speech Recognition error: {e}")

        # ── 2. Priority 2: Whisper via HF Inference API
        if settings.HF_API_KEY:
            try:
                transcript = self._transcribe_hf_whisper(wav_bytes)
                if transcript and transcript.strip():
                    return transcript.strip(), "Whisper (HF API)"
            except Exception as e:
                logger.warning(f"Whisper HF API STT failed: {e}")

        # ── 3. Priority 3: Vosk if model installed locally
        if self.mode == "vosk" or self.vosk_model_dir.exists():
            try:
                transcript = self._transcribe_vosk(wav_bytes)
                if transcript and transcript.strip():
                    return transcript.strip(), "Vosk (Gujarati Model)"
            except Exception as e:
                logger.warning(f"Vosk STT failed: {e}")

        logger.info("No speech recognized or STT services unavailable.")
        return "", "STT Unrecognized"

    def _transcribe_google_speech(self, wav_bytes: bytes) -> Optional[str]:
        """Transcribes WAV audio using Google Speech Recognition API for Gujarati."""
        with sr.AudioFile(io.BytesIO(wav_bytes)) as source:
            audio_data = self._recognizer.record(source)
            # Try Gujarati first
            try:
                text_gu = self._recognizer.recognize_google(audio_data, language="gu-IN")
                if text_gu and text_gu.strip():
                    return text_gu.strip()
            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                logger.warning(f"Google Speech API request error (gu-IN): {e}")

            # Fallback to English (India)
            try:
                text_en = self._recognizer.recognize_google(audio_data, language="en-IN")
                if text_en and text_en.strip():
                    return text_en.strip()
            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                logger.warning(f"Google Speech API request error (en-IN): {e}")

            # Fallback to Hindi (India)
            try:
                text_hi = self._recognizer.recognize_google(audio_data, language="hi-IN")
                if text_hi and text_hi.strip():
                    return text_hi.strip()
            except sr.UnknownValueError:
                pass

            return ""

    def _transcribe_hf_whisper(self, wav_bytes: bytes) -> Optional[str]:
        """Calls Hugging Face Inference API for Whisper with fallback router endpoints."""
        endpoints = [
            f"https://router.huggingface.co/hf-inference/models/{settings.WHISPER_MODEL_ID}",
            f"https://api-inference.huggingface.co/models/{settings.WHISPER_MODEL_ID}",
            "https://router.huggingface.co/hf-inference/models/openai/whisper-small"
        ]
        headers = {"Authorization": f"Bearer {settings.HF_API_KEY}"}

        for api_url in endpoints:
            try:
                resp = requests.post(api_url, headers=headers, data=wav_bytes, timeout=4.0)
                if resp.status_code == 200:
                    res_json = resp.json()
                    if isinstance(res_json, dict) and "text" in res_json:
                        return res_json["text"].strip()
                    elif isinstance(res_json, list) and len(res_json) > 0 and "text" in res_json[0]:
                        return res_json[0]["text"].strip()
            except Exception:
                continue

        return None

    def _transcribe_vosk(self, wav_bytes: bytes) -> Optional[str]:
        """Attempts transcription via local Vosk Gujarati model if installed."""
        if not self.vosk_model_dir.exists():
            return None

        try:
            from vosk import Model, KaldiRecognizer
            model = Model(str(self.vosk_model_dir))
            rec = KaldiRecognizer(model, 16000)
            if rec.AcceptWaveform(wav_bytes):
                import json
                res = json.loads(rec.Result())
                return res.get("text", "").strip()
        except Exception as e:
            logger.warning(f"Vosk STT execution failed: {e}")

        return None


# Global singleton instance
stt_service = STTService()
