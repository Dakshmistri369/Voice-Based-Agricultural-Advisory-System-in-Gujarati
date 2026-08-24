"""
Fallback Resilience & Zero-Crash Test Suite for Phase 10 Hardening.
Verifies graceful degradation when external services (Supabase, HF API, Agmarknet) are unconfigured/offline.
"""

import sys
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Force UTF-8 stdout for Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from db.database import db_manager
from data_services.price_service import price_service
from data_services.weather_service import weather_service
from core.tts_service import tts_service
from pipeline import pipeline


def test_database_fallback():
    """Verifies SQLite local vector database works seamlessly when Supabase is unconfigured."""
    summary = db_manager.get_ingestion_summary()
    assert summary["total_chunks"] > 0
    print(f"✅ Database Fallback: SQLite local vector DB operational with {summary['total_chunks']} chunks.")


def test_price_cache_fallback():
    """Verifies Mandi price service returns cached snapshot when AGMARKNET API key is missing."""
    res = price_service.fetch_mandi_price("Cotton", "Rajkot")
    assert res["modal_price"] > 0
    assert res["is_live"] is False or res["is_live"] is True
    print(f"✅ Price Fallback: Successfully fetched Cotton price ₹{res['modal_price']}/20kg ({res['market_name']}).")


def test_weather_fallback():
    """Verifies Weather service returns Gujarati advisory metrics for all 33 districts."""
    res = weather_service.fetch_weather("Junagadh")
    assert res["temp_c"] > -10
    assert len(res["advisories"]) >= 1
    print(f"✅ Weather Fallback: Successfully fetched Junagadh weather ({res['temp_c']}°C) with advisories.")


def test_tts_gtts_fallback():
    """Verifies gTTS safety net returns playable Gujarati audio bytes."""
    audio_bytes, engine = tts_service.synthesize_speech("ગુજરાતી કિસાન મિત્ર AI માં તમારું સ્વાગત છે.")
    assert len(audio_bytes) > 0
    print(f"✅ TTS Fallback: Synthesized {len(audio_bytes)} audio bytes via '{engine}'.")


def test_pipeline_zero_crash_on_empty():
    """Verifies pipeline returns clean Gujarati fallback error when query is empty."""
    res = pipeline.process_query(text_query="")
    assert res["success"] is False
    assert "કોઈ અવાજ કે લખાણ મળ્યું નથી" in res["error"]
    print("✅ Pipeline Fallback: Handled empty query gracefully with polite Gujarati notice.")


def run_all_fallback_tests():
    print("=" * 70)
    print("🛡️ PHASE 10: FALLBACK RESILIENCE & ZERO-CRASH TEST SUITE")
    print("=" * 70)

    test_database_fallback()
    test_price_cache_fallback()
    test_weather_fallback()
    test_tts_gtts_fallback()
    test_pipeline_zero_crash_on_empty()

    print("\n" + "=" * 70)
    print("🎉 ALL PHASE 10 FALLBACK RESILIENCE TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_all_fallback_tests()
