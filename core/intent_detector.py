"""
Two-Tier Intent Classification Engine for Gujarati Kisaan Mitra AI.
Tier 1: Bilingual Keyword/Lexicon Matching over Gujarati script & Gujlish.
Tier 2: Embedding Cosine Similarity against per-intent anchor phrases.
"""

import json
import logging
import re
from pathlib import Path
from typing import Tuple, Dict, Any, List, Optional
import numpy as np

from config import BASE_DIR
from core.embeddings import embedding_service

logger = logging.getLogger(__name__)


class IntentDetector:
    """Two-Tier Intent Classifier returning (intent, confidence, evidence)."""

    def __init__(self, lexicon_path: Optional[Path] = None):
        self.lexicon_path = lexicon_path or (BASE_DIR / "data" / "intent_lexicon.json")
        self.lexicon = self._load_lexicon()
        self._anchor_embeddings: Dict[str, np.ndarray] = {}
        self._precompute_anchor_embeddings()

    def _load_lexicon(self) -> Dict[str, Any]:
        """Loads bilingual intent lexicon from JSON configuration."""
        if not self.lexicon_path.exists():
            logger.warning(f"Lexicon file missing at {self.lexicon_path}. Using empty lexicon.")
            return {}
        try:
            with open(self.lexicon_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading intent lexicon: {e}")
            return {}

    def _precompute_anchor_embeddings(self):
        """Precomputes vector embeddings for per-intent anchor phrases for Tier 2 classification."""
        for intent, data in self.lexicon.items():
            anchors = data.get("anchor_phrases", [])
            if anchors:
                vecs = embedding_service.embed_text(anchors)
                if len(vecs) > 0:
                    mean_vec = np.mean(vecs, axis=0)
                    mean_vec = mean_vec / (np.linalg.norm(mean_vec) + 1e-10)
                    self._anchor_embeddings[intent] = mean_vec

    def detect_intent(
        self,
        query_text: str,
        english_translation: Optional[str] = None
    ) -> Tuple[str, float, Dict[str, Any]]:
        """
        Classifies user query intent using Tier 1 lexicon matching then Tier 2 embedding similarity.
        Returns: (intent: str, confidence: float, evidence: dict)
        """
        clean_query = query_text.lower().strip()
        combined_text = f"{clean_query} {english_translation.lower() if english_translation else ''}"

        # --- TIER 1: Bilingual Keyword Match ---
        best_tier1_intent = None
        max_score = 0
        matched_keywords = []

        for intent, data in self.lexicon.items():
            score = 0
            current_matches = []
            
            all_keywords = (
                data.get("keywords_gujarati", []) +
                data.get("keywords_english", []) +
                data.get("keywords_gujlish", [])
            )

            for kw in all_keywords:
                pattern = r"\b" + re.escape(kw.lower()) + r"\b"
                if re.search(pattern, combined_text) or kw.lower() in combined_text:
                    score += 1
                    current_matches.append(kw)

            if score > max_score:
                max_score = score
                best_tier1_intent = intent
                matched_keywords = current_matches

        # If high keyword confidence (≥2 matched terms or exact high-weight term)
        if max_score >= 1 and best_tier1_intent:
            confidence = min(0.70 + (max_score * 0.12), 0.98)
            evidence = {
                "tier": "Tier 1 (Lexicon Keyword Match)",
                "matched_keywords": matched_keywords,
                "score": max_score
            }
            return best_tier1_intent, confidence, evidence

        # --- TIER 2: Embedding Cosine Similarity Search ---
        query_vec = embedding_service.embed_query(query_text)
        query_norm = np.linalg.norm(query_vec)
        if query_norm == 0:
            query_norm = 1e-10

        best_tier2_intent = "GENERAL"
        max_sim = 0.0

        for intent, anchor_vec in self.anchor_embeddings.items():
            sim = float(np.dot(query_vec, anchor_vec) / query_norm)
            if sim > max_sim:
                max_sim = sim
                best_tier2_intent = intent

        confidence = round(max_sim, 2)
        evidence = {
            "tier": "Tier 2 (Embedding Cosine Similarity)",
            "similarity_score": confidence,
            "best_anchor_match": best_tier2_intent
        }

        if confidence < 0.40:
            return "GENERAL", confidence, evidence

        return best_tier2_intent, confidence, evidence

    @property
    def anchor_embeddings(self) -> Dict[str, np.ndarray]:
        if not self._anchor_embeddings:
            self._precompute_anchor_embeddings()
        return self._anchor_embeddings


# Global singleton instance
intent_detector = IntentDetector()
