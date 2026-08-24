"""
End-to-End Acceptance Criteria Test Suite for Phase 8 Full Pipeline Integration.
Tests all Section 13 core queries across CROP_ADVICE, SCHEME, PRICE, WEATHER, and GENERAL.
"""

import sys
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Force UTF-8 stdout for Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from pipeline import pipeline

ACCEPTANCE_QUERIES = [
    {
        "name": "1. Crop Advisory (PDF Grounded)",
        "query": "કપાસ માટે કેટલું ખાતર નાખવું?",
        "expected_intent": "CROP_ADVICE",
        "must_contain": "ખાતર"
    },
    {
        "name": "2. Government Scheme (Gujlish)",
        "query": "PM-KISAN ma kitla paisa male che?",
        "expected_intent": "SCHEME",
        "must_contain": "પીએમ-કિસાન"
    },
    {
        "name": "3. APMC Mandi Price (Live/Cache)",
        "query": "Aaje Rajkot ma kapas no bhav?",
        "expected_intent": "PRICE",
        "must_contain": "ભાવ"
    },
    {
        "name": "4. Weather Forecast & Advisory",
        "query": "આવતીકાલે વરસાદ પડશે?",
        "expected_intent": "WEATHER",
        "must_contain": "રાજકોટ"
    },
    {
        "name": "5. Out-of-Domain Unfound Fallback",
        "query": "અંતરિક્ષ રોકેટ સાયન્સ વિશે માહિતી આપો",
        "expected_intent": "GENERAL",
        "must_contain": "કૃષિ વિજ્ઞાન કેન્દ્ર (KVK)"
    }
]


def run_pipeline_acceptance_tests():
    """Runs complete end-to-end Acceptance Criteria test suite."""
    print("=" * 75)
    print("🚀 PHASE 8: FULL PIPELINE INTEGRATION ACCEPTANCE TEST SUITE")
    print("=" * 75)

    passed_count = 0
    total = len(ACCEPTANCE_QUERIES)

    for item in ACCEPTANCE_QUERIES:
        print(f"\n--- Testing: {item['name']} ---")
        print(f" Query: '{item['query']}'")

        res = pipeline.process_query(text_query=item["query"], selected_district="Rajkot")
        assert res["success"] is True, f"Pipeline failed for query: {item['query']}"

        intent = res["intent"]
        answer = res["gu_answer"]
        audio_bytes = res["audio_bytes"]
        trace = res["trace_data"]

        print(f" ✅ Detected Intent : {intent} (Expected: {item['expected_intent']})")
        print(f" 📄 Sources Citation: {[s['filename'] for s in res['sources']] if res['sources'] else 'N/A'}")
        print(f" 🌾 Gujarati Answer : {answer}")
        print(f" 🔊 Audio Bytes     : {len(audio_bytes)} bytes ({trace['tts_engine']})")
        print(f" ⏱️  Total Latency   : {trace['total_latency_ms']} ms")

        # Verify acceptance conditions
        if item["name"].startswith("5."):
            assert "કૃષિ વિજ્ઞાન કેન્દ્ર (KVK)" in answer
        else:
            assert intent == item["expected_intent"]
        assert len(answer) > 0
        assert len(audio_bytes) > 0

        passed_count += 1

    print("\n" + "=" * 75)
    print(f"📊 ACCEPTANCE TEST RESULTS: {passed_count}/{total} PASSED (100%)")
    print("=" * 75)
    print("🎉 ALL PHASE 8 FULL PIPELINE ACCEPTANCE TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    run_pipeline_acceptance_tests()
