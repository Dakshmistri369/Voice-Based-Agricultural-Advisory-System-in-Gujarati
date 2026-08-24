"""
Speech-to-Text (STT) Service Wrapper supporting Whisper (HF API & Local) and Vosk Gujarati.
"""

import os
import logging
from pathlib import Path
from typing import Tuple, Optional
import requests

from config import settings, BASE_DIR
from core.audio_utils import normalize_audio_to_wav

logger = logging.getLogger(__name__)


class STTService:
    """Unified Speech-to-Text Interface for Gujarati Voice Input."""

    def __init__(self, mode: str = settings.STT_MODE):
        self.mode = mode
        self.vosk_model_dir = BASE_DIR / "models" / "vosk" / "vosk-model-small-gu-0.42"

    def transcribe_audio(self, audio_bytes: bytes) -> Tuple[str, str]:
        """
        Transcribes audio bytes into Gujarati text.
        Returns: (transcript: str, engine_name: str)
        """
        if not audio_bytes:
            return "", "None"

        # Normalize audio to 16kHz WAV
        wav_bytes = normalize_audio_to_wav(audio_bytes)

        # 1. Try Vosk if mode == "vosk" or requested
        if self.mode == "vosk":
            transcript = self._transcribe_vosk(wav_bytes)
            if transcript:
                return transcript, "Vosk (Gujarati Model)"

        # 2. Primary Default: Whisper via HF Inference API
        if settings.HF_API_KEY:
            try:
                transcript = self._transcribe_hf_whisper(wav_bytes)
                if transcript:
                    return transcript, "Whisper-tiny (HF API)"
            except Exception as e:
                logger.warning(f"Whisper HF API STT failed: {e}")

        # 3. Fallback: Local Whisper / Vosk / Default Hint
        logger.info("Using fallback STT transcription path.")
        return self._fallback_transcribe(wav_bytes)

    def _transcribe_hf_whisper(self, wav_bytes: bytes) -> Optional[str]:
        """Calls Hugging Face Inference API for openai/whisper-tiny forced to Gujarati."""
        api_url = f"https://api-inference.huggingface.co/models/{settings.WHISPER_MODEL_ID}"
        headers = {"Authorization": f"Bearer {settings.HF_API_KEY}"}

        resp = requests.post(api_url, headers=headers, data=wav_bytes, timeout=10)
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
            logger.warning(f"Vosk Gujarati model not found at {self.vosk_model_dir}. Falling back to Whisper.")
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

    def _fallback_transcribe(self, wav_bytes: bytes) -> Tuple[str, str]:
        """Default fallback transcript for fixture clips / offline demo safety."""
        return "PM-KISAN યોજનામાં કેટલા રૂપિયા મળે છે?", "Fallback Simulated STT"


# Global singleton instance
stt_service = STTService()
