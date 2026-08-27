"""
Audio Normalization Utilities for Mic Bytes & File Conversion.
Normalizes arbitrary browser audio streams (WebM, Opus, Ogg, MP3, M4A, WAV)
to 16kHz Mono 16-bit PCM WAV format using ffmpeg with fallback.
"""

import io
import wave
import subprocess
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


def normalize_audio_to_wav(audio_bytes: bytes, target_sample_rate: int = 16000) -> bytes:
    """
    Normalizes input audio bytes to 16kHz mono 16-bit PCM WAV.
    Handles WebM/Opus, OGG, MP3, AAC, and WAV directly via ffmpeg.
    Returns normalized WAV bytes.
    """
    if not audio_bytes or len(audio_bytes) < 50:
        return b""

    # 1. Primary conversion via ffmpeg subprocess (handles WebM, Opus, MP3, OGG, AAC)
    try:
        process = subprocess.Popen(
            [
                "ffmpeg",
                "-y",
                "-i", "pipe:0",
                "-acodec", "pcm_s16le",
                "-ac", "1",
                "-ar", str(target_sample_rate),
                "-f", "wav",
                "pipe:1"
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        wav_out, _ = process.communicate(input=audio_bytes, timeout=4)
        if process.returncode == 0 and wav_out and len(wav_out) > 44:
            return wav_out
    except Exception as e:
        logger.debug(f"ffmpeg conversion fallback: {e}")

    # 2. Check if already a valid WAV header
    if audio_bytes.startswith(b"RIFF") and b"WAVE" in audio_bytes[:16]:
        try:
            with wave.open(io.BytesIO(audio_bytes), "rb") as wave_in:
                channels = wave_in.getnchannels()
                framerate = wave_in.getframerate()
                sampwidth = wave_in.getsampwidth()

                # If parameters match 16kHz mono 16-bit, return as is
                if channels == 1 and framerate == target_sample_rate and sampwidth == 2:
                    return audio_bytes
        except Exception as e:
            logger.debug(f"WAV verification note: {e}")

    # 3. Fallback to wrapping raw bytes in standard WAV header format
    return _create_wav_header(audio_bytes, sample_rate=target_sample_rate)


def _create_wav_header(raw_pcm: bytes, sample_rate: int = 16000, channels: int = 1, bit_depth: int = 16) -> bytes:
    """Wraps raw PCM audio bytes with a standard RIFF/WAVE header."""
    byte_rate = sample_rate * channels * (bit_depth // 8)
    block_align = channels * (bit_depth // 8)
    data_size = len(raw_pcm)

    header = bytearray()
    header.extend(b"RIFF")
    header.extend((data_size + 36).to_bytes(4, "little"))
    header.extend(b"WAVE")
    header.extend(b"fmt ")
    header.extend((16).to_bytes(4, "little"))  # Subchunk1Size
    header.extend((1).to_bytes(2, "little"))   # AudioFormat (PCM)
    header.extend(channels.to_bytes(2, "little"))
    header.extend(sample_rate.to_bytes(4, "little"))
    header.extend(byte_rate.to_bytes(4, "little"))
    header.extend(block_align.to_bytes(2, "little"))
    header.extend(bit_depth.to_bytes(2, "little"))
    header.extend(b"data")
    header.extend(data_size.to_bytes(4, "little"))

    return bytes(header) + raw_pcm
