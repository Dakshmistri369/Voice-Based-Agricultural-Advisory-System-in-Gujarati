"""
Tesseract OCR Service Wrapper with Gujarati (guj) and English (eng) support.
"""

import io
import logging
from typing import Optional
from PIL import Image

try:
    import pytesseract
except ImportError:
    pytesseract = None

logger = logging.getLogger(__name__)


class OCRService:
    """Tesseract OCR wrapper handling Gujarati and English text extraction from images."""

    def __init__(self, languages: str = "guj+eng"):
        self.languages = languages
        self.is_available = self._check_tesseract_availability()

    def _check_tesseract_availability(self) -> bool:
        """Verifies if pytesseract and Tesseract binary are installed."""
        if pytesseract is None:
            logger.warning("pytesseract package is not installed.")
            return False
        try:
            # Check tesseract version
            _ = pytesseract.get_tesseract_version()
            return True
        except Exception as e:
            logger.warning(f"Tesseract OCR binary not found or not in PATH: {e}")
            return False

    def extract_text_from_image(self, image: Image.Image) -> str:
        """Extracts text from a PIL Image using combined language packs (guj+eng)."""
        if not self.is_available:
            logger.warning("Tesseract OCR is unavailable. Skipping OCR extraction.")
            return ""

        try:
            # Custom config for page segmentation mode 3 (Fully automatic page segmentation)
            custom_config = f"-l {self.languages} --psm 3"
            extracted_text = pytesseract.image_to_string(image, config=custom_config)
            return extracted_text.strip()
        except Exception as e:
            logger.error(f"OCR Extraction Error: {e}")
            return ""


# Instantiate singleton instance
ocr_service = OCRService()
