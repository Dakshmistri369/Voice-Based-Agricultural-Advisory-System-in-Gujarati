"""
Scheme Browser — aggregates scheme chunks from the database by category.
Uses the same db_manager.search_similar_chunks backend as the RAG pipeline.
"""

import logging
import re
from typing import List, Dict, Any

from core.embeddings import embedding_service
from db.database import db_manager

logger = logging.getLogger(__name__)

SCHEME_KEYWORDS = {
    "Central":   ["PM-KISAN", "pradhan mantri", "central", "KCC", "PMFBY"],
    "Gujarat":   ["Gujarat", "Mukhyamantri", "GSAMB"],
    "Insurance": ["insurance", "PMFBY", "WBCIS", "crop insurance"],
    "Credit":    ["KCC", "Kisan Credit", "loan", "credit"],
    "Subsidy":   ["subsidy", "sahay", "shaxam"],
}


def list_all_schemes(district: str = None, category_filter: str = "All") -> List[Dict[str, Any]]:
    """
    Retrieves scheme-category chunks and groups them by source document.
    Falls back to a broad scheme-related query if category filtering returns nothing.
    """
    try:
        query_vec = embedding_service.embed_query("government scheme farmers Gujarat benefit yojana")
        raw_chunks = db_manager.search_similar_chunks(
            query_vector=query_vec,
            doc_category="scheme",
            top_k=80
        )
    except Exception as e:
        logger.warning(f"Scheme browser DB search failed: {e}")
        raw_chunks = []

    # Fall back to unfiltered search if no scheme-tagged chunks
    if not raw_chunks:
        try:
            query_vec = embedding_service.embed_query("scheme yojana farmer benefit")
            raw_chunks = db_manager.search_similar_chunks(
                query_vector=query_vec,
                doc_category=None,
                top_k=40
            )
        except Exception as e:
            logger.warning(f"Scheme browser fallback search failed: {e}")
            raw_chunks = []

    # Group chunks by source filename
    grouped: Dict[str, List[str]] = {}
    for chunk in raw_chunks:
        fname = chunk.get("source_filename", "Unknown")
        grouped.setdefault(fname, []).append(chunk.get("chunk_text", ""))

    schemes = []
    for fname, chunks in grouped.items():
        combined = " ".join(chunks[:3])
        name = _extract_name(fname)
        benefit = _extract_benefit(combined)
        cat = _classify(fname + " " + combined)
        if category_filter != "All" and cat != category_filter:
            continue
        schemes.append({
            "name":            name,
            "benefit":         benefit,
            "detail_text":     combined[:600],
            "source_filename": fname,
            "category":        cat
        })

    return schemes


def _extract_name(filename: str) -> str:
    name = filename.replace(".pdf", "").replace("_", " ").replace("-", " ").strip()
    return name[:60].title() + ("…" if len(name) > 60 else "")


def _extract_benefit(text: str) -> str:
    m = re.search(r"(₹[\d,]+|Rs\.?\s*[\d,]+|\d+[\d,]*\s*(?:crore|lakh|rupees?))", text, re.IGNORECASE)
    if m:
        return m.group(0)
    m2 = re.search(r"(\d+%)", text)
    if m2:
        return m2.group(0)
    return "—"


def _classify(text: str) -> str:
    text_lower = text.lower()
    for cat, keywords in SCHEME_KEYWORDS.items():
        if any(kw.lower() in text_lower for kw in keywords):
            return cat
    return "Central"
