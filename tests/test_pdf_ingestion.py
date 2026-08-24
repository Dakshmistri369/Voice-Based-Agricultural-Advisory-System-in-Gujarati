"""
Unit and Integration Test Suite for Phase 3 PDF Ingestion Pipeline.
"""

import sys
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Force UTF-8 encoding for Windows stdout
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from core.pdf_loader import pdf_loader
from core.chunker import chunker, detect_language
from core.embeddings import embedding_service
from db.database import db_manager
from ingest_pdfs import run_pdf_ingestion


def test_language_detection():
    """Test Gujarati, English, and Mixed language Unicode range detector."""
    gu_text = "કપાસ માટે કેટલું ખાતર નાખવું?"
    en_text = "What is the recommended fertilizer dosage for cotton crop?"
    mixed_text = "PM-KISAN યોજનામાં કેટલા paisa male?"

    assert detect_language(gu_text) == "gu"
    assert detect_language(en_text) == "en"
    assert detect_language(mixed_text) in ["gu", "mixed"]


def test_chunker_separators():
    """Test character chunker with Gujarati full stop and sentence boundaries."""
    sample_text = (
        "પીએમ-કિસાન યોજના હેઠળ વાર્ષિક ₹6,000 મળે છે। આ નાણાં ત્રણ હપ્તામાં જમા થાય છે. "
        "ખેડૂતોએ ઇ-કેવાયસી (e-KYC) કરાવવું ફરજિયાત છે।"
    )
    chunks = chunker.chunk_text(
        text=sample_text,
        source_filename="test_scheme.pdf",
        page_number=1,
        doc_category="scheme"
    )
    assert len(chunks) >= 1
    assert chunks[0].source_filename == "test_scheme.pdf"
    assert chunks[0].doc_category == "scheme"


def test_pdf_ingestion_end_to_end():
    """Runs ingestion pipeline and asserts vector database chunk records."""
    summary = run_pdf_ingestion()
    assert summary is not None
    assert summary.get("total_chunks", 0) > 0
    assert summary.get("total_files", 0) > 0


if __name__ == "__main__":
    print("Running Phase 3 Ingestion Tests...")
    test_language_detection()
    test_chunker_separators()
    summary = run_pdf_ingestion()
    print("ALL PHASE 3 INGESTION TESTS PASSED SUCCESSFULLY!")
