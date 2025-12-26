"""
Excel/spreadsheet extractor plugin.
"""

import logging
from typing import List

from ..plugins.base import Extractor

logger = logging.getLogger(__name__)


class ExcelExtractor(Extractor, name="excel"):
    """
    Excel and spreadsheet extractor.
    
    Converts spreadsheet data to a text representation suitable for LLM processing.
    
    Attributes:
        mime_types: MIME types this extractor handles
        priority: Extraction priority
    """
    
    mime_types = [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
        "application/vnd.ms-excel",  # .xls
        "text/csv",
        "application/csv",
    ]
    priority = 50
    
    def extract(self, file_path: str) -> str:
        """
        Extract text from a spreadsheet file.
        
        Args:
            file_path: Path to the spreadsheet file
            
        Returns:
            Text representation of the spreadsheet data
        """
        from ..documents.spreadsheet import spreadsheet_to_text
        return spreadsheet_to_text(file_path)
    
    def can_handle(self, mime_type: str) -> bool:
        """Check if this extractor can handle the given MIME type."""
        return mime_type in self.mime_types
