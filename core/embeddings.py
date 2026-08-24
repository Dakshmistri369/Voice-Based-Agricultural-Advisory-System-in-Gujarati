"""
Embedding Generator Wrapper utilizing BAAI/bge-m3 (1024-dimension multilingual).
"""

import logging
from typing import List, Union
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

from config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Embedding model wrapper for BAAI/bge-m3 producing 1024-dim vector embeddings."""

    def __init__(self, model_name: str = settings.EMBEDDING_MODEL_ID):
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        """Lazy loads SentenceTransformer model to avoid startup delay."""
        if self._model is None:
            if SentenceTransformer is not None:
                logger.info(f"Loading SentenceTransformer model: {self.model_name}")
                try:
                    self._model = SentenceTransformer(self.model_name)
                except Exception as e:
                    logger.warning(f"Could not load {self.model_name} locally: {e}. Fallback to dummy vectors.")
                    self._model = None
            else:
                logger.warning("sentence-transformers package not available.")
                self._model = None
        return self._model

    def embed_text(self, text: Union[str, List[str]]) -> np.ndarray:
        """Generates 1024-dimensional vector embeddings for text or list of texts."""
        if isinstance(text, str):
            texts = [text]
        else:
            texts = text

        if not texts:
            return np.array([], dtype=np.float32)

        if self.model is not None:
            try:
                embeddings = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
                return embeddings
            except Exception as e:
                logger.error(f"Error encoding embeddings: {e}")

        # Fallback to pseudo-random normalized 1024-dim vectors based on text hash for offline testing
        logger.info("Using deterministic fallback vector encoder.")
        vectors = []
        for t in texts:
            seed = abs(hash(t)) % (2**32)
            rng = np.random.RandomState(seed)
            vec = rng.randn(1024).astype(np.float32)
            vec = vec / (np.linalg.norm(vec) + 1e-10)
            vectors.append(vec)

        return np.array(vectors, dtype=np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        """Generates embedding vector for a user search query."""
        res = self.embed_text([query])
        return res[0] if len(res) > 0 else np.zeros(1024, dtype=np.float32)


# Singleton instance
embedding_service = EmbeddingService()
