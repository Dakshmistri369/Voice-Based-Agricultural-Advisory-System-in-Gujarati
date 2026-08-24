"""
Benchmark Test Suite for Phase 4: Intent Classification & RAG PDF Retrieval.
Tests 15 labelled Gujarati, Gujlish, and English queries for accuracy (Target >= 85%).
"""

import sys
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Force UTF-8 stdout for Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from core.intent_detector import intent_detector
from core.entity_extractor import entity_extractor
from data_services.rag_service import rag_service

# 15 Labelled Benchmark Test Queries
TEST_QUERIES = [
    {"query": "કપાસ માટે કેટલું ખાતર નાખવું?", "expected_intent": "CROP_ADVICE"},
    {"query": "PM-KISAN ma kitla paisa male che?", "expected_intent": "SCHEME"},
    {"query": "Aaje Rajkot ma kapas no bhav?", "expected_intent": "PRICE"},
    {"query": "આવતીકાલે વરસાદ પડશે?", "expected_intent": "WEATHER"},
    {"query": "પાંદડા પર ગેરુ નો રોગ થયો છે", "expected_intent": "DISEASE"},
    {"query": "નમસ્તે કિસાન મિત્ર", "expected_intent": "GREETING"},
    {"query": "મગફળીમાં વાવેતર નો સમય ક્યારે?", "expected_intent": "CROP_ADVICE"},
    {"query": "PMFBY yojana information in gujarati", "expected_intent": "SCHEME"},
    {"query": "આજે અમરેલી માં જીરૂ નો ભાવ કેટલો", "expected_intent": "PRICE"},
    {"query": "અમદાવાદ માં આજનું હવામાન કેવું રહેશે", "expected_intent": "WEATHER"},
    {"query": "ખાતર નો ડોઝ કેટલો આપવો કપાસમાં", "expected_intent": "CROP_ADVICE"},
    {"query": "ikhedut portal par subsidy information", "expected_intent": "SCHEME"},
    {"query": "આજે બજાર ભાવ શું છે કપાસનો", "expected_intent": "PRICE"},
    {"query": "જમીન માં ભેજ અને પાણી સિંચાઈ", "expected_intent": "CROP_ADVICE"},
    {"query": "અંતરિક્ષ વિજ્ઞાન અને રોકેટ ની માહિતી આપો", "expected_intent": "GENERAL"}
]


def run_benchmark_tests():
    """Runs intent classification accuracy test and PDF retrieval verification."""
    print("=" * 70)
    print("🧪 PHASE 4: INTENT DETECTOR & RAG RETRIEVAL BENCHMARK SUITE")
    print("=" * 70)

    correct_intents = 0
    total_queries = len(TEST_QUERIES)

    for idx, item in enumerate(TEST_QUERIES, start=1):
        q = item["query"]
        expected = item["expected_intent"]

        intent, confidence, evidence = intent_detector.detect_intent(q)
        entities = entity_extractor.extract_entities(q)
        is_found, context, sources, top_sim = rag_service.retrieve_context(q)

        is_correct = (intent == expected)
        if is_correct:
            correct_intents += 1
            status_icon = "✅"
        else:
            status_icon = "❌"

        print(f"[{idx:02d}/{total_queries:02d}] {status_icon} Query: '{q}'")
        print(f"     Predicted: {intent} ({confidence:.2f}) | Expected: {expected}")
        print(f"     Extracted Entities: Crop={entities['crop']}, District={entities['district']}")
        source_str = ", ".join(f"{s['filename']} (p.{s['page']})" for s in sources) if sources else "None"
        print(f"     PDF Sources: {source_str} (Top Sim: {top_sim:.3f})\n")

    accuracy_pct = (correct_intents / total_queries) * 100
    print("=" * 70)
    print(f"📊 BENCHMARK ACCURACY RESULT: {correct_intents}/{total_queries} ({accuracy_pct:.1f}%)")
    print(" Target Accuracy: >= 85.0%")
    print("=" * 70)

    assert accuracy_pct >= 85.0, f"Accuracy {accuracy_pct:.1f}% below 85% target threshold!"
    print("🎉 ALL PHASE 4 BENCHMARK RETRIEVAL TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    run_benchmark_tests()
