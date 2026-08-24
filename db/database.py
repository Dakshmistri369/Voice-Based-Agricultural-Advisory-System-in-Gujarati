"""
Database Management Layer with Dual-Path Architecture: Supabase/PostgreSQL pgvector 
with automatic Local SQLite + Numpy Cosine Search Fallback.
"""

import json
import logging
import sqlite3
from typing import List, Dict, Any, Optional
import numpy as np

from config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages document chunk insertion, deletion, and vector search operations."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = str(db_path or settings.LOCAL_DB_PATH)
        self.use_supabase = bool(settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY)
        self._supabase_client = None

        # Ensure database directory exists
        settings.LOCAL_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._init_sqlite_db()

    def _init_sqlite_db(self):
        """Initializes local SQLite tables for offline vector & metadata storage."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_filename TEXT NOT NULL,
                    doc_category TEXT NOT NULL,
                    page_number INTEGER NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    chunk_text TEXT NOT NULL,
                    detected_language TEXT NOT NULL,
                    char_count INTEGER NOT NULL,
                    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    embedding_json TEXT NOT NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_doc_cat_source 
                ON document_chunks (doc_category, source_filename)
                """
            )
            conn.commit()
        logger.info(f"SQLite local fallback database initialized at {self.db_path}")

    def delete_chunks_by_filename(self, filename: str) -> int:
        """Deletes existing chunks for a given source filename before re-ingesting."""
        deleted_count = 0
        # Delete from local SQLite
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM document_chunks WHERE source_filename = ?", (filename,))
            deleted_count = cursor.rowcount
            conn.commit()

        # Delete from Supabase if configured
        if self.use_supabase:
            try:
                from supabase import create_client
                client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
                _ = client.table("document_chunks").delete().eq("source_filename", filename).execute()
            except Exception as e:
                logger.warning(f"Supabase delete failed for {filename}: {e}")

        return deleted_count

    def insert_document_chunks(self, chunks: List[Dict[str, Any]], embeddings: np.ndarray) -> int:
        """Inserts document chunks and vector embeddings into SQLite and Supabase."""
        if not chunks or len(chunks) != len(embeddings):
            raise ValueError("Chunks count must match embeddings count.")

        inserted_count = 0

        # Insert into Local SQLite
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for chunk, emb in zip(chunks, embeddings):
                emb_json = json.dumps(emb.tolist())
                cursor.execute(
                    """
                    INSERT INTO document_chunks (
                        source_filename, doc_category, page_number, chunk_index,
                        chunk_text, detected_language, char_count, embedding_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        chunk["source_filename"],
                        chunk["doc_category"],
                        chunk["page_number"],
                        chunk["chunk_index"],
                        chunk["chunk_text"],
                        chunk["language"],
                        chunk["char_count"],
                        emb_json,
                    ),
                )
            inserted_count = len(chunks)
            conn.commit()

        # Insert into Supabase if configured
        if self.use_supabase:
            try:
                from supabase import create_client
                client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
                records = []
                for chunk, emb in zip(chunks, embeddings):
                    rec = chunk.copy()
                    rec["embedding"] = emb.tolist()
                    records.append(rec)
                _ = client.table("document_chunks").insert(records).execute()
                logger.info(f"Inserted {len(records)} records into Supabase.")
            except Exception as e:
                logger.warning(f"Supabase batch insert failed: {e}")

        return inserted_count

    def search_similar_chunks(
        self,
        query_vector: np.ndarray,
        doc_category: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Vector similarity search over document_chunks using numpy cosine similarity."""
        results: List[Dict[str, Any]] = []

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if doc_category:
                cursor.execute(
                    "SELECT * FROM document_chunks WHERE doc_category = ?", (doc_category,)
                )
            else:
                cursor.execute("SELECT * FROM document_chunks")

            rows = cursor.fetchall()
            if not rows:
                return []

            # Compute Cosine Similarity
            query_norm = np.linalg.norm(query_vector)
            if query_norm == 0:
                query_norm = 1e-10

            scored_chunks = []
            for row in rows:
                emb_list = json.loads(row["embedding_json"])
                emb = np.array(emb_list, dtype=np.float32)
                emb_norm = np.linalg.norm(emb)
                if emb_norm == 0:
                    emb_norm = 1e-10

                similarity = float(np.dot(query_vector, emb) / (query_norm * emb_norm))

                chunk_dict = {
                    "id": row["id"],
                    "source_filename": row["source_filename"],
                    "doc_category": row["doc_category"],
                    "page_number": row["page_number"],
                    "chunk_index": row["chunk_index"],
                    "chunk_text": row["chunk_text"],
                    "detected_language": row["detected_language"],
                    "char_count": row["char_count"],
                    "similarity": similarity,
                }
                scored_chunks.append(chunk_dict)

            # Sort by similarity descending
            scored_chunks.sort(key=lambda x: x["similarity"], reverse=True)
            results = scored_chunks[:top_k]

        return results

    def get_ingestion_summary(self) -> Dict[str, Any]:
        """Returns statistical summary report of ingested documents."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM document_chunks")
            total_chunks = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(DISTINCT source_filename) FROM document_chunks")
            total_files = cursor.fetchone()[0]

            cursor.execute(
                "SELECT detected_language, COUNT(*) FROM document_chunks GROUP BY detected_language"
            )
            lang_counts = dict(cursor.fetchall())

            cursor.execute(
                "SELECT doc_category, COUNT(*) FROM document_chunks GROUP BY doc_category"
            )
            cat_counts = dict(cursor.fetchall())

        return {
            "total_files": total_files,
            "total_chunks": total_chunks,
            "language_breakdown": lang_counts,
            "category_breakdown": cat_counts,
        }


# Global database instance
db_manager = DatabaseManager()
