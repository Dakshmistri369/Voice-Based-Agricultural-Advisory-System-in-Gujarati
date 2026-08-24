"""
PyMuPDF PDF Loader with Automatic Tesseract OCR Fallback for Scanned Pages.
"""

import io
import logging
from pathlib import Path
from typing import List, Dict, Any
from PIL import Image

try:
    import pymupdf as fitz  # PyMuPDF
except ImportError:
    try:
        import fitz
    except ImportError:
        fitz = None

from core.ocr_service import ocr_service

logger = logging.getLogger(__name__)


class PDFPageResult:
    """Container for extracted page content and metadata."""

    def __init__(self, page_number: int, text: str, is_ocr_used: bool = False):
        self.page_number = page_number
        self.text = text
        self.is_ocr_used = is_ocr_used
        self.char_count = len(text)


class PDFLoader:
    """PDF Text Extractor with 300 DPI rendering OCR fallback for image pages."""

    def __init__(self, min_text_length_threshold: int = 50):
        self.min_text_length_threshold = min_text_length_threshold

    def extract_pdf_pages(self, pdf_path: Path) -> List[PDFPageResult]:
        """Extracts text page-by-page from a PDF file using PyMuPDF and OCR fallback."""
        if fitz is None:
            raise ImportError("PyMuPDF (fitz) is not installed. Please run pip install PyMuPDF.")

        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        results: List[PDFPageResult] = []

        try:
            doc = fitz.open(pdf_path)
            for page_idx, page in enumerate(doc, start=1):
                # Primary PyMuPDF text extraction
                extracted_text = page.get_text("text").strip()
                is_ocr_used = False

                # Fallback to OCR if extracted text length is below threshold
                if len(extracted_text) < self.min_text_length_threshold:
                    logger.info(f"Page {page_idx} of {pdf_path.name} below threshold ({len(extracted_text)} chars). Triggering OCR.")
                    
                    # Render page at 300 DPI for optimal OCR accuracy
                    dpi_scale = 300 / 72
                    mat = fitz.Matrix(dpi_scale, dpi_scale)
                    pix = page.get_pixmap(matrix=mat)
                    
                    # Convert fitz pixmap to PIL Image
                    img_bytes = pix.tobytes("png")
                    image = Image.open(io.BytesIO(img_bytes))
                    
                    ocr_text = ocr_service.extract_text_from_image(image)
                    if len(ocr_text) > len(extracted_text):
                        extracted_text = ocr_text
                        is_ocr_used = True

                results.append(
                    PDFPageResult(
                        page_number=page_idx,
                        text=extracted_text,
                        is_ocr_used=is_ocr_used
                    )
                )

            doc.close()
        except Exception as e:
            logger.error(f"Error reading PDF {pdf_path.name}: {e}")
            raise e

        return results


# Global singleton instance
pdf_loader = PDFLoader()
