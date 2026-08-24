"""
CLI Test Suite for Phase 6 Language Core: Full End-to-End gu -> en -> RAG -> LLM -> gu Chain.
Prints per-stage latencies in milliseconds and cites grounding PDF sources.
"""

import sys
import time
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Force UTF-8 stdout for Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from core.transliterator import transliterator
from core.translator import translator_service
from core.intent_detector import intent_detector
from data_services.rag_service import rag_service
from core.llm_service import llm_service

SAMPLE_QUESTIONS = [
    "PM-KISAN યોજનામાં વાર્ષિક કેટલા રૂપિયા મળે છે?",
    "કપાસ માટે કેટલું ખાતર નાખવું?",
    "આજે રાજકોટ માં કપાસનો બજાર ભાવ કેટલો?",
    "આવતીકાલે વરસાદ પડશે?",
    "અંતરિક્ષ રોકેટ વિજ્ઞાન ની માહિતી આપો"
]


def test_language_chain():
    """Executes 5 sample questions through the full Language Core chain."""
    print("=" * 75)
    print("🌐 PHASE 6: LANGUAGE CORE FULL END-TO-END CHAIN TEST")
    print("=" * 75)

    for idx, raw_query in enumerate(SAMPLE_QUESTIONS, start=1):
        print(f"\n--- [QUESTION {idx}/5]: '{raw_query}' ---")
        t0 = time.time()

        # Stage 1: Script Normalization & Transliterator
        t1_start = time.time()
        norm_query = transliterator.normalize_text(raw_query)
        t1_ms = int((time.time() - t1_start) * 1000)

        # Stage 2: Translation gu -> en
        t2_start = time.time()
        en_query = translator_service.translate_gu_to_en(norm_query)
        t2_ms = int((time.time() - t2_start) * 1000)

        # Stage 3: Intent Classification
        t3_start = time.time()
        intent, conf, evidence = intent_detector.detect_intent(norm_query, en_query)
        t3_ms = int((time.time() - t3_start) * 1000)

        # Stage 4: PDF RAG Context Retrieval
        t4_start = time.time()
        doc_category = "scheme" if intent == "SCHEME" else ("crop_advisory" if intent == "CROP_ADVICE" else None)
        is_found, context, sources, top_sim = rag_service.retrieve_context(en_query, doc_category=doc_category)
        t4_ms = int((time.time() - t4_start) * 1000)

        # Stage 5: Grounded LLM Generation & en -> gu Translation
        t5_start = time.time()
        en_ans, gu_ans, val_meta = llm_service.generate_grounded_answer(en_query, context, is_found)
        t5_ms = int((time.time() - t5_start) * 1000)

        total_ms = int((time.time() - t0) * 1000)

        # Print Trace Output
        print(f" 1. Normalized Query: {norm_query} ({t1_ms} ms)")
        print(f" 2. English Pivot   : {en_query} ({t2_ms} ms)")
        print(f" 3. Detected Intent : {intent} (Conf: {conf:.2f}) ({t3_ms} ms)")
        source_str = ", ".join(f"{s['filename']} (p.{s['page']})" for s in sources) if sources else "None"
        print(f" 4. PDF Grounding   : {source_str} (Top Sim: {top_sim:.3f}) ({t4_ms} ms)")
        print(f" 5. English Answer  : {en_ans[:100]}...")
        print(f" 6. Gujarati Answer : {gu_ans} ({t5_ms} ms)")
        print(f" ⏱️  Stage Latencies : gu2en={t2_ms}ms | RAG={t4_ms}ms | LLM+en2gu={t5_ms}ms | TOTAL={total_ms}ms")
        print(f" 🛡️  Validation     : Script OK={val_meta['is_gujarati_script']} | Grounded={val_meta['is_grounded']}")

        # Assertions
        assert gu_ans is not None and len(gu_ans) > 0
        assert val_meta["is_gujarati_script"] is True

    print("\n" + "=" * 75)
    print("🎉 ALL PHASE 6 LANGUAGE CORE PIPELINE TESTS PASSED SUCCESSFULLY!")
    print("=" * 75)


if __name__ == "__main__":
    test_language_chain()
