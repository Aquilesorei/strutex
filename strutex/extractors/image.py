"""
Image extractor plugin using OCR.
"""

import logging
from typing import List

from ..plugins.base import Extractor

logger = logging.getLogger(__name__)

# Check for OCR dependencies
try:
    import pytesseract
    from PIL import Image
    _OCR_AVAILABLE = True
except ImportError:
    _OCR_AVAILABLE = False


class ImageExtractor(Extractor, name="image"):
    """
    Image extractor using Tesseract OCR.
    
    Requires pytesseract and PIL to be installed.
    Install with: pip install strutex[ocr]
    
    Attributes:
        mime_types: MIME types this extractor handles
        priority: Extraction priority
    """
    
    mime_types = [
        "image/png",
        "image/jpeg", 
        "image/jpg",
        "image/tiff",
        "image/bmp",
        "image/gif",
    ]
    priority = 50
    
    def extract(self, file_path: str) -> str:
        """
        Extract text from an image using OCR.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Extracted text content
            
        Raises:
            RuntimeError: If OCR dependencies are not installed
        """
        if not _OCR_AVAILABLE:
            raise RuntimeError(
                "OCR dependencies not installed. "
                "Install with: pip install strutex[ocr]"
            )
        
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            logger.error(f"OCR extraction failed for {file_path}: {e}")
            raise RuntimeError(f"Failed to extract text from image: {e}")
    
    def can_handle(self, mime_type: str) -> bool:
        """Check if this extractor can handle the given MIME type."""
        return mime_type in self.mime_types
    
    @classmethod
    def health_check(cls) -> bool:
        """Check if OCR dependencies are available."""
        return _OCR_AVAILABLE
