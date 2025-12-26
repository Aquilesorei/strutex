
"""
Tests for FormattedDocExtractor (v0.8.0).
"""

import sys
import os
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from strutex.extractors.formatted import FormattedDocExtractor, ExtractionError

class TestFormattedExtractorConfig:
    def test_init_validation(self):
        # Valid
        FormattedDocExtractor()
        
        # Invalid validation
        with pytest.raises(ValueError):
            FormattedDocExtractor(line_margin=-1)
        with pytest.raises(ValueError):
            FormattedDocExtractor(char_margin=0)
        with pytest.raises(ValueError):
            FormattedDocExtractor(filter_tolerance=-0.1)
        with pytest.raises(ValueError):
            FormattedDocExtractor(max_table_rows=0)
        with pytest.raises(ValueError):
            FormattedDocExtractor(table_format="json")

class TestFormattedHelpers:
    def setup_method(self):
        self.extractor = FormattedDocExtractor()

    def test_preserve_indentation(self):
        raw = "Title\n    Subtitle\n        Point 1"
        processed = self.extractor._preserve_indentation(raw)
        
        # Should normalize indentation using 4-space blocks
        assert processed == "Title\n  Subtitle\n    Point 1"
        
        # Handle empty
        assert self.extractor._preserve_indentation("") == ""

    def test_validate_layout(self):
        assert self.extractor._validate_layout("Valid text\nWith lines") is True
        assert self.extractor._validate_layout("") is False
        
        # Recurring char pattern
        assert self.extractor._validate_layout("aaaaaaaaaaaaaaaaaaaaa") is False
        
        # Long lines
        long_line = "a" * 600
        assert self.extractor._validate_layout(long_line) is False

    def test_format_table_markdown(self):
        self.extractor.table_format = "markdown"
        data = [
            ["ID", "Name"],
            ["1", "Alice"],
            ["2", "Bob"]
        ]
        result = self.extractor._format_table(data)
        assert "| ID | Name |" in result
        assert "| --- | --- |" in result
        assert "| 1 | Alice |" in result

    def test_format_table_csv(self):
        self.extractor.table_format = "csv"
        data = [
            ["ID", "Name"],
            ["1", "Alice, Smith"]
        ]
        result = self.extractor._format_table(data)
        assert "```csv" in result
        assert "ID,Name" in result
        assert '1,"Alice, Smith"' in result

    def test_format_table_plain(self):
        self.extractor.table_format = "plain"
        data = [
            ["ID", "Name"],
            ["1", "Alice"]
        ]
        result = self.extractor._format_table(data)
        assert "ID\tName" in result
        assert "1\tAlice" in result

    def test_format_table_truncation(self):
        self.extractor.max_table_rows = 1
        data = [
            ["H"], ["R1"], ["R2"]
        ]
        result = self.extractor._format_table(data)
        # Should have Header, R1, and truncation marker
        assert "..." in result
        assert "R2" not in result

class TestExtractionFlow:
    @patch("strutex.extractors.formatted.pdfplumber")
    def test_extract_calls_pdfplumber(self, mock_plumber):
        # Mock pdfplumber open context manager
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        
        # Setup mocks for page methods
        mock_page.extract_text.return_value = "Extracted Text"
        mock_page.find_tables.return_value = []
        mock_page.filter.return_value.extract_text.return_value = "Extracted Text"
        
        # Allow crop (header/footer detection)
        mock_page.crop.return_value = mock_page
        
        mock_pdf.pages = [mock_page]
        
        mock_plumber.open.return_value.__enter__.return_value = mock_pdf
        
        extractor = FormattedDocExtractor()
        with patch("os.path.exists", return_value=True):
            result = extractor.extract("doc.pdf")
        
        assert "Extracted Text" in result
        assert "--- Page 1 (digital) ---" in result

    def test_extract_missing_file(self):
        extractor = FormattedDocExtractor(raise_on_error=True)
        with pytest.raises(FileNotFoundError):
            extractor.extract("missing.pdf")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
