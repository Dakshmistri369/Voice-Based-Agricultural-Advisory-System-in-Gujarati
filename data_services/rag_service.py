"""
RAG Service: Document Retrieval, Similarity Reranking, Quality Filtering, and Context Formatting.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

from config import settings
from core.embeddings import embedding_service
from db.database import db_manager

logger = logging.getLogger(__name__)

STRICT_FALLBACK_GUJARATI = (
    "મને આ વિષય પર પૂરતી માહિતી નથી. કૃપા કરી તમારા નજીકના કૃષિ વિજ્ઞાન કેન્દ્ર (KVK) નો સંપર્ક કરો."
)

BOILERPLATE_PATTERNS = [
    r"creative\s+commons",
    r"licensed\s+under",
    r"all\s+rights\s+reserved",
    r"isbn[:\s]",
    r"issn[:\s]",
    r"doi:\s*10\.",
    r"table\s+of\s+contents",
    r"index\s+of\s+authors",
    r"published\s+by",
    r"printed\s+in",
]


def is_boilerplate_chunk(text: str) -> bool:
    """Detects if a chunk contains only copyright, license, or catalog metadata."""
    t_lower = text.lower().strip()
    if len(t_lower) < 60:
        return True
    for pattern in BOILERPLATE_PATTERNS:
        if re.search(pattern, t_lower):
            # If the chunk is short and mentions license/copyright, it's boilerplate
            if len(t_lower) < 250 or t_lower.count("\n") < 3:
                return True
    return False


class RAGService:
    """Document Chunk Retrieval and Context Formatter for Grounded Generation."""

    def __init__(self, similarity_threshold: float = settings.SIMILARITY_THRESHOLD):
        self.similarity_threshold = similarity_threshold

    def retrieve_context(
        self,
        query_text: str,
        doc_category: Optional[str] = None,
        top_k: int = settings.TOP_K_RETRIEVAL
    ) -> Tuple[bool, str, List[Dict[str, Any]], float]:
        """
        Retrieves top relevant PDF document chunks for a user query.
        Returns: (is_found: bool, context_text: str, sources: list, top_similarity_score: float)
        """
        if not query_text.strip():
            return False, STRICT_FALLBACK_GUJARATI, [], 0.0

        # Step 1: Embed query vector
        query_vector = embedding_service.embed_query(query_text)

        # Step 2: Search similar chunks in document_chunks vector store
        raw_chunks = db_manager.search_similar_chunks(
            query_vector=query_vector,
            doc_category=doc_category,
            top_k=top_k * 3  # Retrieve extra candidate pool for filtering & deduplication
        )

        if not raw_chunks:
            logger.info("Vector search returned 0 chunks.")
            return False, STRICT_FALLBACK_GUJARATI, [], 0.0

        # Step 3: Filter boilerplate & Re-rank & Deduplicate by (filename, page_number)
        seen_pages = set()
        reranked_chunks: List[Dict[str, Any]] = []

        for chunk in raw_chunks:
            # Skip boilerplate / copyright metadata chunks
            if is_boilerplate_chunk(chunk.get("chunk_text", "")):
                continue

            page_key = (chunk["source_filename"], chunk["page_number"])
            if page_key in seen_pages:
                continue
            seen_pages.add(page_key)

            # Apply category match boost
            score = chunk["similarity"]
            if doc_category and chunk["doc_category"] == doc_category:
                score += 0.05

            chunk["final_score"] = score
            reranked_chunks.append(chunk)

        # Sort by final score descending
        reranked_chunks.sort(key=lambda x: x["final_score"], reverse=True)
        top_chunks = reranked_chunks[:top_k]

        if not top_chunks:
            return False, STRICT_FALLBACK_GUJARATI, [], 0.0

        top_similarity = top_chunks[0]["similarity"]

        # Step 4: Check minimum similarity threshold
        if top_similarity < self.similarity_threshold:
            logger.info(f"Top chunk similarity ({top_similarity:.3f}) below threshold ({self.similarity_threshold}). Triggering KVK fallback.")
            return False, STRICT_FALLBACK_GUJARATI, [], top_similarity

        # Step 5: Format context block for LLM prompt
        context_blocks = []
        sources = []

        for c in top_chunks:
            tag = f"[Source: {c['source_filename']}, Page {c['page_number']}]"
            context_blocks.append(f"{tag}\n{c['chunk_text']}")
            sources.append({
                "filename": c["source_filename"],
                "page": c["page_number"],
                "similarity": round(c["similarity"], 3),
                "category": c["doc_category"]
            })

        formatted_context = "\n\n".join(context_blocks)
        return True, formatted_context, sources, top_similarity


# Global singleton instance
rag_service = RAGService()
