"""
Recursive Text Chunker with Gujarati Unicode Language Detection & Metadata Tagging.
"""

import re
from typing import List, Dict, Any, Literal

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    RecursiveCharacterTextSplitter = None


def detect_language(text: str) -> Literal["gu", "en", "mixed"]:
    """
    Detects language based on Unicode character ranges.
    Gujarati Unicode block: U+0A80 to U+0AFF.
    """
    if not text.strip():
        return "en"

    # Count Gujarati Unicode characters
    gujarati_chars = len(re.findall(r"[\u0A80-\u0AFF]", text))
    # Count English ASCII alphabetic characters
    english_chars = len(re.findall(r"[a-zA-Z]", text))
    total_alpha = gujarati_chars + english_chars

    if total_alpha == 0:
        return "gu" if gujarati_chars > 0 else "en"

    gu_ratio = gujarati_chars / total_alpha
    en_ratio = english_chars / total_alpha

    if gu_ratio > 0.6:
        return "gu"
    elif en_ratio > 0.6:
        return "en"
    else:
        return "mixed"


class DocumentChunk:
    """Container for a single text chunk with metadata."""

    def __init__(
        self,
        chunk_text: str,
        source_filename: str,
        page_number: int,
        doc_category: str,
        chunk_index: int,
        language: str,
    ):
        self.chunk_text = chunk_text
        self.source_filename = source_filename
        self.page_number = page_number
        self.doc_category = doc_category
        self.chunk_index = chunk_index
        self.language = language
        self.char_count = len(chunk_text)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_text": self.chunk_text,
            "source_filename": self.source_filename,
            "page_number": self.page_number,
            "doc_category": self.doc_category,
            "chunk_index": self.chunk_index,
            "language": self.language,
            "char_count": self.char_count,
        }


class Chunker:
    """Recursive Character Chunker tuned for Gujarati and English agricultural texts."""

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 120):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Custom separators including Gujarati full stop (।) and sentence boundaries
        self.separators = ["\n\n", "\n", "।", ".", "!", "?", ",", " ", ""]

    def chunk_text(
        self,
        text: str,
        source_filename: str,
        page_number: int,
        doc_category: str,
        start_chunk_index: int = 0
    ) -> List[DocumentChunk]:
        """Splits page text into document chunks with full metadata."""
        if not text.strip():
            return []

        # Split text into chunks using LangChain splitter if available, else custom split
        if RecursiveCharacterTextSplitter is not None:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                separators=self.separators
            )
            raw_chunks = splitter.split_text(text)
        else:
            raw_chunks = self._fallback_split(text)

        chunks: List[DocumentChunk] = []
        for idx, raw_chunk in enumerate(raw_chunks, start=start_chunk_index):
            cleaned_text = raw_chunk.strip()
            if not cleaned_text:
                continue

            lang = detect_language(cleaned_text)
            chunks.append(
                DocumentChunk(
                    chunk_text=cleaned_text,
                    source_filename=source_filename,
                    page_number=page_number,
                    doc_category=doc_category,
                    chunk_index=idx,
                    language=lang,
                )
            )

        return chunks

    def _fallback_split(self, text: str) -> List[str]:
        """Simple fallback splitter when LangChain is unavailable."""
        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = start + self.chunk_size
            if end >= text_len:
                chunks.append(text[start:])
                break
            
            # Find nearest sentence terminator or newline
            break_pos = max(
                text.rfind("\n", start, end),
                text.rfind("।", start, end),
                text.rfind(".", start, end)
            )
            if break_pos == -1 or break_pos <= start:
                break_pos = end

            chunks.append(text[start:break_pos])
            start = max(start + 1, break_pos - self.chunk_overlap)

        return chunks


# Global singleton instance
chunker = Chunker()
