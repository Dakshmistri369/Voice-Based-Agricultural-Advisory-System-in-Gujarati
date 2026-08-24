"""
CLI Test Suite for Phase 7 Voice I/O: STT Transcription & Cascading TTS Speech Synthesis.
"""

import sys
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Force UTF-8 stdout for Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from core.audio_utils import normalize_audio_to_wav
from core.stt_service import stt_service
from core.tts_service import tts_service


def run_voice_io_tests():
    """Executes Voice I/O unit and integration tests."""
    print("=" * 70)
    print("🎙️ PHASE 7: VOICE I/O (STT & TTS) VERIFICATION")
    print("=" * 70)

    # 1. Test Audio Normalization
    print("\n--- 1. TESTING AUDIO NORMALIZATION ---")
    raw_pcm = b"\x00\x01" * 16000  # 1 second of pseudo 16kHz PCM
    wav_bytes = normalize_audio_to_wav(raw_pcm)
    assert wav_bytes.startswith(b"RIFF")
    print(f"✅ PCM bytes ({len(raw_pcm)} bytes) -> Normalized WAV ({len(wav_bytes)} bytes with RIFF header).")

    # 2. Test Speech-to-Text (STT) Service
    print("\n--- 2. TESTING SPEECH-TO-TEXT (STT) ENGINE ---")
    transcript, stt_engine = stt_service.transcribe_audio(wav_bytes)
    print(f"✅ STT Engine Used : {stt_engine}")
    print(f"   Transcribed Text: '{transcript}'")
    assert len(transcript) > 0

    # 3. Test Text-to-Speech (TTS) Service Cascade
    print("\n--- 3. TESTING TEXT-TO-SPEECH (TTS) CASCADE ---")
    test_gujarati_text = "પીએમ-કિસાન યોજના હેઠળ તમામ પાત્ર ખેડૂતોને વાર્ષિક ₹6,000 ત્રણ સમાન હપ્તામાં સીધા બેંક ખાતામાં મળે છે."
    audio_bytes, tts_engine = tts_service.synthesize_speech(test_gujarati_text)
    
    print(f"✅ TTS Engine Served: {tts_engine}")
    print(f"   Generated Audio : {len(audio_bytes)} bytes")
    assert len(audio_bytes) > 0, "TTS failed to synthesize audio bytes!"

    print("\n" + "=" * 70)
    print("🎉 ALL PHASE 7 VOICE I/O TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_voice_io_tests()
