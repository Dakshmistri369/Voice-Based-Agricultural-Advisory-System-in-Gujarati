"""
Speech-to-Text (STT) Service Wrapper supporting Google Speech Recognition (gu-IN),
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

    def transcribe_audio(self, audio_bytes: bytes) -> Tuple[str, str]:
        """
        Transcribes audio bytes into Gujarati text.
        Returns: (transcript: str, engine_name: str)
        """
        if not audio_bytes or len(audio_bytes) < 100:
            return "", "None"

        # Normalize audio to 16kHz Mono WAV
        wav_bytes = normalize_audio_to_wav(audio_bytes)

        # ── 1. Priority 1: Google Speech Recognition (gu-IN) (Fast, accurate, free)
        if self._recognizer is not None:
            try:
                transcript = self._transcribe_google_speech(wav_bytes)
                if transcript and transcript.strip():
                    return transcript.strip(), "Google Speech Recognition (gu-IN)"
            except Exception as e:
                logger.warning(f"Google Speech Recognition error: {e}")

        # ── 2. Priority 2: Vosk if mode == 'vosk' or installed locally
        if self.mode == "vosk" or self.vosk_model_dir.exists():
            try:
                transcript = self._transcribe_vosk(wav_bytes)
                if transcript and transcript.strip():
                    return transcript.strip(), "Vosk (Gujarati Model)"
            except Exception as e:
                logger.warning(f"Vosk STT failed: {e}")

        # ── 3. Priority 3: Whisper via HF Inference API (2.0s timeout)
        if settings.HF_API_KEY:
            try:
                transcript = self._transcribe_hf_whisper(wav_bytes)
                if transcript and transcript.strip():
                    return transcript.strip(), "Whisper-tiny (HF API)"
            except Exception as e:
                logger.warning(f"Whisper HF API STT failed: {e}")

        # ── 4. Fallback Hint for Demo / Unrecognized Speech
        logger.info("No speech recognized or STT services unavailable.")
        return "", "STT Unrecognized"

    def _transcribe_google_speech(self, wav_bytes: bytes) -> Optional[str]:
        """Transcribes WAV audio using Google Speech Recognition API for Gujarati."""
        with sr.AudioFile(io.BytesIO(wav_bytes)) as source:
            # Adjust for ambient noise if needed
            audio_data = self._recognizer.record(source)
            try:
                # Try Gujarati first
                return self._recognizer.recognize_google(audio_data, language="gu-IN")
            except sr.UnknownValueError:
                # Fallback to English (India) in case farmer spoke in Gujlish/English
                try:
                    return self._recognizer.recognize_google(audio_data, language="en-IN")
                except sr.UnknownValueError:
                    return ""
            except sr.RequestError as e:
                logger.warning(f"Google Speech API request error: {e}")
                return ""

    def _transcribe_hf_whisper(self, wav_bytes: bytes) -> Optional[str]:
        """Calls Hugging Face Inference API for Whisper with strict 2.0s timeout."""
        api_url = f"https://api-inference.huggingface.co/models/{settings.WHISPER_MODEL_ID}"
        headers = {"Authorization": f"Bearer {settings.HF_API_KEY}"}

        resp = requests.post(api_url, headers=headers, data=wav_bytes, timeout=2.0)
        if resp.status_code == 200:
            res_json = resp.json()
            if isinstance(res_json, dict):
                return res_json.get("text", "").strip()
            elif isinstance(res_json, list) and len(res_json) > 0:
                return res_json[0].get("text", "").strip()

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
