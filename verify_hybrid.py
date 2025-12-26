from strutex import DocumentProcessor, Object, String, HybridProvider, HybridStrategy, Provider
import os
from unittest.mock import MagicMock

# Mock Primary Provider that fails on file but works on text
class FlakyProvider(Provider):
    def process(self, file_path, prompt, schema, mime_type, **kwargs):
        if file_path.endswith(".pdf"):
            raise ValueError("File upload failed!")
        elif file_path.endswith(".txt"):
            return {"status": "success", "content": "extracted from text"}
        else:
            raise ValueError(f"Unknown file: {file_path}")

    async def aprocess(self, file_path, prompt, schema, mime_type, **kwargs):
        if file_path.endswith(".pdf"):
            raise ValueError("File upload failed!")
        elif file_path.endswith(".txt"):
            return {"status": "success", "content": "extracted from text"}
        else:
            raise ValueError(f"Unknown file: {file_path}")

def test_hybrid_fallback():
    print("\n--- Testing Hybrid Fallback ---")
    
    # Mock extract_text because we don't have a real PDF here
    # We'll monkeypatch for the test
    HybridProvider._extract_text = lambda self, path, mime: "This is some extracted text"
    
    hybrid = HybridProvider(primary_provider=FlakyProvider())
    processor = DocumentProcessor(provider=hybrid)
    
    # Create dummy PDF
    with open("dummy.pdf", "w") as f: f.write("dummy")
    
    try:
        result = processor.process("dummy.pdf", "Extract", Object(properties={"status": String()}))
        print("Result:", result)
        assert result["status"] == "success"
        print("Hybrid Fallback Passed!")
    finally:
        os.remove("dummy.pdf")

if __name__ == "__main__":
    test_hybrid_fallback()
