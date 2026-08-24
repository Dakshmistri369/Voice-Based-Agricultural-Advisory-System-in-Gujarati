"""
Standalone PDF Document Ingestion CLI for Gujarati Kisaan Mitra AI.
Converts PDFs under data/pdfs/ into page-level chunks, extracts text via PyMuPDF/OCR,
generates embeddings, and upserts into the document_chunks vector database.
"""

import sys
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, List

# Reconfigure stdout for Windows UTF-8 Gujarati output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from config import settings, BASE_DIR
from core.pdf_loader import pdf_loader
from core.chunker import chunker
from core.embeddings import embedding_service
from db.database import db_manager

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("PDF_Ingestion")


def organize_root_pdfs():
    """Moves any loose PDFs from the root folder into data/pdfs/ subfolders."""
    root_dir = BASE_DIR
    target_crop = settings.PDF_DIR / "crop_advisory"
    target_scheme = settings.PDF_DIR / "schemes"
    target_general = settings.PDF_DIR / "general"

    target_crop.mkdir(parents=True, exist_ok=True)
    target_scheme.mkdir(parents=True, exist_ok=True)
    target_general.mkdir(parents=True, exist_ok=True)

    for pdf_file in root_dir.glob("*.pdf"):
        filename_lower = pdf_file.name.lower()
        if "એગ્રીકલ્ચર" in pdf_file.name or "crop" in filename_lower or "book" in filename_lower:
            dest = target_crop / pdf_file.name
        elif "scheme" in filename_lower or "kisan" in filename_lower or "yojana" in filename_lower:
            dest = target_scheme / pdf_file.name
        else:
            dest = target_general / pdf_file.name

        logger.info(f"Organizing loose PDF '{pdf_file.name}' -> {dest.relative_to(root_dir)}")
        shutil.copy2(pdf_file, dest)


def determine_category(pdf_path: Path) -> str:
    """Determines document category from folder location or filename."""
    parent_name = pdf_path.parent.name.lower()
    if parent_name in ["schemes", "scheme"]:
        return "scheme"
    elif parent_name in ["crop_advisory", "crop", "advisory"]:
        return "crop_advisory"
    else:
        # Check filename heuristics
        fname = pdf_path.name.lower()
        if "scheme" in fname or "yojana" in fname or "kisan" in fname:
            return "scheme"
        elif " crop" in fname or "એગ્રીકલ્ચર" in fname or "advisory" in fname:
            return "crop_advisory"
        return "general"


def run_pdf_ingestion() -> Dict[str, Any]:
    """Executes end-to-end ingestion pipeline over all discovered PDFs."""
    print("=" * 70)
    print("🚀 GUJARATI KISAAN MITRA AI — PDF DOCUMENT INGESTION PIPELINE")
    print("=" * 70)

    # 1. Organize loose PDFs if present
    organize_root_pdfs()

    # 2. Discover PDFs recursively
    pdf_files = list(settings.PDF_DIR.rglob("*.pdf"))
    if not pdf_files:
        print("⚠️ No PDF files found under data/pdfs/ directory.")
        return {}

    print(f"📄 Discovered {len(pdf_files)} PDF document(s) for ingestion.\n")

    total_pages_processed = 0
    total_ocr_pages = 0
    total_chunks_created = 0
    files_summary: List[Dict[str, Any]] = []

    for pdf_path in pdf_files:
        category = determine_category(pdf_path)
        filename = pdf_path.name

        print(f" Processing [{category.upper()}]: {filename}...")

        try:
            # Step 1: Extract pages (PyMuPDF + OCR fallback)
            pages = pdf_loader.extract_pdf_pages(pdf_path)
            ocr_count = sum(1 for p in pages if p.is_ocr_used)
            total_pages_processed += len(pages)
            total_ocr_pages += ocr_count

            # Step 2: Chunk pages with recursive character splitter
            pdf_chunks = []
            chunk_counter = 0
            for page in pages:
                page_chunks = chunker.chunk_text(
                    text=page.text,
                    source_filename=filename,
                    page_number=page.page_number,
                    doc_category=category,
                    start_chunk_index=chunk_counter
                )
                chunk_counter += len(page_chunks)
                pdf_chunks.extend(page_chunks)

            if not pdf_chunks:
                print(f"  ⚠️ Warning: No readable text chunks generated for {filename}")
                continue

            # Step 3: Generate embeddings using BAAI/bge-m3
            chunk_dicts = [c.to_dict() for c in pdf_chunks]
            chunk_texts = [c.chunk_text for c in pdf_chunks]
            embeddings = embedding_service.embed_text(chunk_texts)

            # Step 4: Delete existing & upsert into document_chunks table
            _ = db_manager.delete_chunks_by_filename(filename)
            inserted_count = db_manager.insert_document_chunks(chunk_dicts, embeddings)
            total_chunks_created += inserted_count

            files_summary.append({
                "filename": filename,
                "category": category,
                "pages": len(pages),
                "ocr_pages": ocr_count,
                "chunks": inserted_count
            })

            print(f"  ✅ Extracted {len(pages)} pages ({ocr_count} OCR) -> {inserted_count} vector chunks ingested.")

        except Exception as e:
            print(f"  ❌ Failed to ingest {filename}: {e}")
            logger.error(f"Error ingesting {filename}", exc_info=True)

    # 3. Print Comprehensive Ingestion Summary Report
    print("\n" + "=" * 70)
    print("📊 INGESTION SUMMARY REPORT")
    print("=" * 70)
    print(f" Total PDF Files Processed: {len(files_summary)}")
    print(f" Total Pages Read        : {total_pages_processed} ({total_ocr_pages} via Tesseract OCR)")
    print(f" Total Vector Chunks     : {total_chunks_created}")

    db_summary = db_manager.get_ingestion_summary()
    print(f" Language Breakdown       : {db_summary.get('language_breakdown', {})}")
    print(f" Category Breakdown       : {db_summary.get('category_breakdown', {})}")
    print("=" * 70)

    return db_summary


if __name__ == "__main__":
    run_pdf_ingestion()
