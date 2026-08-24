"""
Cascading Text-to-Speech (TTS) Engine for Gujarati Audio Generation.
Fallback Cascade: Piper TTS (Local ONNX) -> HF MMS-TTS -> gTTS (Safety Net).
"""

import io
import os
import subprocess
import logging
from pathlib import Path
from typing import Tuple, Optional
import requests

try:
    from gtts import gTTS
except ImportError:
    gTTS = None

from config import settings, BASE_DIR

logger = logging.getLogger(__name__)


class TTSService:
    """Cascading Text-to-Speech Interface for Gujarati Audio Output."""

    def __init__(self):
        self.piper_model_dir = BASE_DIR / "models" / "piper"
        self.piper_onnx = self.piper_model_dir / "gu_IN-cpm-medium.onnx"

    def synthesize_speech(self, gujarati_text: str) -> Tuple[bytes, str]:
        """
        Synthesizes Gujarati text into audio bytes.
        Returns: (audio_bytes: bytes, engine_name: str)
        """
        text = gujarati_text.strip()
        if not text:
            return b"", "None"

        # Priority 1: Hugging Face Arjun4707/piper-gujarati-male TTS Model
        if settings.HF_API_KEY:
            try:
                audio_bytes = self._synthesize_hf_piper_gujarati(text)
                if audio_bytes:
                    return audio_bytes, f"Piper Gujarati Male TTS ({settings.TTS_MODEL_ID})"
            except Exception as e:
                logger.warning(f"Piper Gujarati HF TTS synthesis failed: {e}")

        # Priority 2: Piper Local ONNX Model (if weights installed locally)
        if self.piper_onnx.exists():
            try:
                audio_bytes = self._synthesize_piper_local(text)
                if audio_bytes:
                    return audio_bytes, "Piper TTS (Local ONNX gu_IN)"
            except Exception as e:
                logger.warning(f"Local Piper ONNX synthesis failed: {e}")

        # Priority 3: Hugging Face MMS-TTS for Gujarati (facebook/mms-tts-guj)
        if settings.HF_API_KEY:
            try:
                audio_bytes = self._synthesize_hf_mms_tts(text)
                if audio_bytes:
                    return audio_bytes, "HF MMS-TTS (facebook/mms-tts-guj)"
            except Exception as e:
                logger.warning(f"HF MMS-TTS synthesis failed: {e}")

        # Priority 4: gTTS (Google Text-to-Speech) Safety Net
        if gTTS is not None:
            try:
                audio_bytes = self._synthesize_gtts(text)
                if audio_bytes:
                    return audio_bytes, "gTTS (Gujarati Safety Net)"
            except Exception as e:
                logger.warning(f"gTTS synthesis failed: {e}")

        logger.error("All TTS engines failed or unavailable.")
        return b"", "TTS Unavailable"

    def _synthesize_hf_piper_gujarati(self, text: str) -> Optional[bytes]:
        """Queries Hugging Face Inference API for Arjun4707/piper-gujarati-male model."""
        api_url = f"https://api-inference.huggingface.co/models/{settings.TTS_MODEL_ID}"
        headers = {"Authorization": f"Bearer {settings.HF_API_KEY}"}
        payload = {"inputs": text}

        resp = requests.post(api_url, headers=headers, json=payload, timeout=8)
        if resp.status_code == 200 and len(resp.content) > 100:
            return resp.content

        return None

    def _synthesize_piper_local(self, text: str) -> Optional[bytes]:
        """Synthesizes audio using Piper ONNX binary/subprocess."""
        output_wav = self.piper_model_dir / "temp_output.wav"

        # Command: echo "text" | piper --model model.onnx --output_file output.wav
        cmd = [
            "piper",
            "--model", str(self.piper_onnx),
            "--output_file", str(output_wav)
        ]

        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, _ = process.communicate(input=text.encode("utf-8"))

        if output_wav.exists():
            with open(output_wav, "rb") as f:
                data = f.read()
            output_wav.unlink(missing_ok=True)
            return data

        return None

    def _synthesize_hf_mms_tts(self, text: str) -> Optional[bytes]:
        """Queries HF Inference API for facebook/mms-tts-guj."""
        api_url = "https://api-inference.huggingface.co/models/facebook/mms-tts-guj"
        headers = {"Authorization": f"Bearer {settings.HF_API_KEY}"}
        payload = {"inputs": text}

        resp = requests.post(api_url, headers=headers, json=payload, timeout=8)
        if resp.status_code == 200 and len(resp.content) > 100:
            return resp.content

        return None

    def _synthesize_gtts(self, text: str) -> Optional[bytes]:
        """Generates audio via gTTS (lang='gu')."""
        tts = gTTS(text=text, lang="gu", slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()


# Global singleton instance
tts_service = TTSService()
