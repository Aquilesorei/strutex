"""Tests for DocumentInput class."""
import io
import os
import tempfile
import pytest

from strutex.input import DocumentInput


class TestDocumentInput:
    """Test DocumentInput class."""
    
    def test_from_file_path_string(self, tmp_path):
        """Test creation from file path string."""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"PDF content")
        
        doc = DocumentInput(str(test_file))
        
        assert doc.is_file_path is True
        assert doc.path == str(test_file)
        assert doc.filename == "test.pdf"
    
    def test_from_path_object(self, tmp_path):
        """Test creation from Path object."""
        test_file = tmp_path / "invoice.pdf"
        test_file.write_bytes(b"PDF content")
        
        doc = DocumentInput(test_file)
        
        assert doc.is_file_path is True
        assert doc.filename == "invoice.pdf"
    
    def test_from_bytesio(self):
        """Test creation from BytesIO."""
        data = io.BytesIO(b"PDF content")
        
        doc = DocumentInput(data, filename="upload.pdf")
        
        assert doc.is_file_path is False
        assert doc.path is None
        assert doc.filename == "upload.pdf"
    
    def test_as_file_path_with_file(self, tmp_path):
        """Test as_file_path context manager with file path."""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"PDF content")
        
        doc = DocumentInput(str(test_file))
        
        with doc.as_file_path() as path:
            assert path == str(test_file)
            assert os.path.exists(path)
    
    def test_as_file_path_with_bytesio(self):
        """Test as_file_path creates temp file for BytesIO."""
        data = io.BytesIO(b"PDF content here")
        doc = DocumentInput(data, filename="upload.pdf")
        
        with doc.as_file_path() as path:
            # Temp file should exist
            assert os.path.exists(path)
            assert path.endswith(".pdf")
            
            # Content should match
            with open(path, "rb") as f:
                assert f.read() == b"PDF content here"
        
        # Temp file should be cleaned up
        assert not os.path.exists(path)
    
    def test_get_bytes_from_file(self, tmp_path):
        """Test get_bytes from file path."""
        test_file = tmp_path / "test.txt"
        test_file.write_bytes(b"Hello World")
        
        doc = DocumentInput(str(test_file))
        
        assert doc.get_bytes() == b"Hello World"
    
    def test_get_bytes_from_bytesio(self):
        """Test get_bytes from BytesIO."""
        data = io.BytesIO(b"Content from memory")
        doc = DocumentInput(data)
        
        assert doc.get_bytes() == b"Content from memory"
    
    def test_get_mime_type_pdf(self):
        """Test MIME type detection for PDF."""
        doc = DocumentInput(io.BytesIO(b""), filename="invoice.pdf")
        assert doc.get_mime_type() == "application/pdf"
    
    def test_get_mime_type_png(self):
        """Test MIME type detection for PNG."""
        doc = DocumentInput(io.BytesIO(b""), filename="image.png")
        assert doc.get_mime_type() == "image/png"
    
    def test_get_mime_type_xlsx(self):
        """Test MIME type detection for Excel."""
        doc = DocumentInput(io.BytesIO(b""), filename="data.xlsx")
        assert doc.get_mime_type() == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    def test_get_mime_type_explicit_override(self):
        """Test explicit MIME type override."""
        doc = DocumentInput(io.BytesIO(b""), filename="file.dat", mime_type="application/octet-stream")
        assert doc.get_mime_type() == "application/octet-stream"
    
    def test_get_mime_type_unknown(self):
        """Test unknown extension returns None."""
        doc = DocumentInput(io.BytesIO(b""), filename="file.unknown")
        assert doc.get_mime_type() is None
    
    def test_repr_file_path(self, tmp_path):
        """Test string representation for file path."""
        doc = DocumentInput(str(tmp_path / "test.pdf"))
        assert "path" in repr(doc)
        assert "test.pdf" in repr(doc)
    
    def test_repr_bytesio(self):
        """Test string representation for BytesIO."""
        doc = DocumentInput(io.BytesIO(b""), filename="upload.pdf")
        assert "bytes" in repr(doc)
        assert "upload.pdf" in repr(doc)
