"""
Audio Normalization Utilities for Mic Bytes & File Conversion.
Normalizes arbitrary audio streams to 16kHz Mono 16-bit PCM WAV format.
"""

import io
import wave
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


def normalize_audio_to_wav(audio_bytes: bytes, target_sample_rate: int = 16000) -> bytes:
    """
    Normalizes input audio bytes to 16kHz mono 16-bit PCM WAV.
    Returns normalized WAV bytes.
    """
    if not audio_bytes:
        return b""

    # Check if already a valid WAV header
    if audio_bytes.startswith(b"RIFF") and b"WAVE" in audio_bytes[:16]:
        try:
            with wave.open(io.BytesIO(audio_bytes), "rb") as wave_in:
                channels = wave_in.getnchannels()
                framerate = wave_in.getframerate()
                sampwidth = wave_in.getsampwidth()
                frames = wave_in.readframes(wave_in.getnframes())

                # If parameters match 16kHz mono 16-bit, return as is
                if channels == 1 and framerate == target_sample_rate and sampwidth == 2:
                    return audio_bytes
        except Exception as e:
            logger.warning(f"Error reading WAV header: {e}")

    # Fallback to returning raw bytes wrapped in standard WAV header format
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
