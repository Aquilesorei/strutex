"""
PDF Extractor implementation using pdfplumber.
"""

from typing import Optional
import logging
from ..plugins.base import Extractor

logger = logging.getLogger("strutex.extractors.pdf")

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False


class PDFExtractor(Extractor, name="pdfplumber"):
    """
    Extracts text from PDF files using pdfplumber.
    
    Robust fallback when multimodal LLM processing fails.
    """
    
    priority = 80
    supported_mime_types = ["application/pdf"]
    
    def extract(self, file_path: str) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text content from all pages
        """
        if not PDFPLUMBER_AVAILABLE:
            raise ImportError("pdfplumber is required for PDFExtractor. Install with: pip install pdfplumber")
            
        text_content = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(f"--- Page {i+1} ---\n{page_text}")
            
            return "\n\n".join(text_content)
            
        except Exception as e:
            logger.error(f"Failed to extract text from {file_path}: {e}")
            raise RuntimeError(f"PDF extraction failed: {e}") from e
            
    @classmethod
    def health_check(cls) -> bool:
        return PDFPLUMBER_AVAILABLE
